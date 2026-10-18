// Run only against your own disposable staging system. RATE sets completed surveys/sec.
import http from 'k6/http';
import {check} from 'k6';
import crypto from 'k6/crypto';
export const options = {
  scenarios: {submissions: {executor:'constant-arrival-rate', rate:Number(__ENV.RATE || 20), timeUnit:'1s', duration:__ENV.DURATION || '60s', preAllocatedVUs:50, maxVUs:500}},
  thresholds: {'http_req_failed':['rate<0.01'], 'http_req_duration{operation:submit}':['p(95)<500','p(99)<1500'], checks:['rate>0.99'], dropped_iterations:['count==0']}
};
const base = __ENV.BASE_URL || 'http://localhost:8080';
export function setup() {
  const response = http.get(`${base}/api/v1/survey`);
  if(response.status!==200) throw new Error('Survey unavailable');
  return response.json();
}
export default function(survey) {
  const raw=crypto.sha256(crypto.randomBytes(16),'hex').slice(0,32);
  const key=`${raw.slice(0,8)}-${raw.slice(8,12)}-4${raw.slice(13,16)}-a${raw.slice(17,20)}-${raw.slice(20)}`;
  const answers=Object.fromEntries(survey.questions.map(q=>[q.id,q.options[Math.floor(Math.random()*q.options.length)].id]));
  const body=JSON.stringify({survey_version:survey.version,catalog_version:survey.catalog_version,category:'all',mode:survey.mode,seed:survey.seed,answers});
  const parameters={headers:{'Content-Type':'application/json','Idempotency-Key':key},tags:{operation:'submit'}};
  const response=http.post(`${base}/api/v1/matches`,body,parameters);
  check(response,{'saved':r=>r.status===200,'five reasons':r=>r.status===200 && r.json().matches[0].reasons.length===5});
  if(__ITER%10===0 && response.status===200) {
    const replay=http.post(`${base}/api/v1/matches`,body,{...parameters,tags:{operation:'replay'}});
    check(replay,{'replay identical':r=>r.status===200 && r.body===response.body,'marked replay':r=>r.headers['Idempotency-Replayed']==='true'});
  }
}
