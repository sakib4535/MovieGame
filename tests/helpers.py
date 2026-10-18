from uuid import uuid4

def key():
    return {'Idempotency-Key': str(uuid4())}

def payload(client, category='all', mode='story'):
    survey = client.get('/api/v1/survey', params={'mode':mode}).json()
    return {'survey_version': survey['version'], 'catalog_version': survey['catalog_version'],
            'category': category, 'mode':mode, 'seed':survey['seed'],
            'answers': {q['id']: q['options'][i % len(q['options'])]['id'] for i,q in enumerate(survey['questions'])}}
