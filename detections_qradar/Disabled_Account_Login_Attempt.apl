SELECT username, sourceip, destinationip, qidname(qid)
FROM events 
WHERE qidname(qid) ILIKE '%disabled account%' OR eventid = '4725' OR eventid = '4625'
LAST 1 HOURS
