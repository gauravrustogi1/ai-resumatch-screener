import json

import ollama

def main():
    jd = getFileContent('job_description.txt')
    resumeMarkup = getFileContent('RESUME.md')
    myPrompt = setMyPrompt(jd, resumeMarkup)
    llmResult = getLLMMatchResults(myPrompt)
    llmResultSanitised = sanitiseLLMResult(llmResult)
    print("-x-"*50, "\n\n\nSanitised Result:", llmResultSanitised)
    print("-x-"*50, "\n\n\nSanitised Result Type :", type(llmResultSanitised))


def setMyPrompt(jd, resumeMarkup):
    myPrompt = """
You are a recruitment specialist. You need to compare given Job-Description with Resume.


Job-Description:
-----------------

"""
    myPrompt += jd
    myPrompt += """


Resume (in Markdown format):
----------------------------

"""
    myPrompt += resumeMarkup
    myPrompt += """



Processing Instructions:
------------------------
Match the requirements from Job Description with my resume. Dont just rely on keywords but try to match the gist.
I want you to give me a match score out of 10 on following criteria
1. qualification
2. work experience
3. domain
4. Overall

Provide as a JSON array of short bullet-point strings (each under ~100 characters), 6-7 bullets for each of:
1. why do you think this Job Description matches my Resume 
2. What specific requirements are missing from my resume but required in Job Description


Output Structure:
-----------------
{
	"scores":{
		"qualification": integer
		, "work_experience": integer
		, "domain": integer
		, "overall": integer
	}
	, "what_matches_well": ["bullet point 1", "bullet point 2", ...]
	, "what_is_missing": ["bullet point 1", "bullet point 2", ...]
}


Output Validation:
------------------
I want the output STRICTLY in JSON ONLY. do not add even a single character apart from JSON in the output
After generation of output do following
1. check if output is a valid json object
2. check if output has exactly the keys given in the json structure above. None missing and No extra key added
3. confirm that the keys 'scores', 'what_matches_well', 'what_is_missing' are present in the JSON
4. Do not prepend ```json to the output. 
5. Do not add any other text other than JSON. No confirmation on validation, or notification telling here is the processed output. 
6. No asking for any other help. 
7. Strictly the JSON and JSON only... not a single character extra
8. Do not provide any explanation whatsoever outside JSON structure defined above.


IMPORTANT:
Ensure that the output from you is pure JSON and valid JSON only .... i will be passing it to my code directly assuming its JSON so if u return a single extra character, my script will fail.
"""
    return myPrompt

def getLLMMatchResults(myPrompt):
    response = ollama.chat(model='llama3.1:8b', messages=[
        {'role': 'user', 'content': myPrompt}
    ])
    return response.message.content

def sanitiseLLMResult(llmResult):
    returnValue = ''
    start = llmResult.find('{')
    end = llmResult.rfind('}')
    returnValue = validateJSON( llmResult[start:end+1] )
    return returnValue


def validateJSON(llmResult):
    returnValue = {}
    try:
        returnValue = json.loads(llmResult)
    except Exception as e:
        print("Error in JSON validation:", e)
        return None
    try:
        keys = sorted(returnValue.keys())
        requiredKeys = sorted(['scores', 'what_matches_well', 'what_is_missing'])
        if keys != requiredKeys:
            raise KeyError
    except KeyError:
        print("Error: JSON keys do not match the required structure. | ", llmResult)
        return None
    return returnValue


def getFileContent(fileName):
    with open(fileName, 'r') as f:
        return f.read()


if __name__ == '__main__':
    main()