import json
#beam try
import transformers
from transformers import pipeline
import torch

pipe = pipeline(
    "text-generation",
    model="HuggingFaceH4/zephyr-7b-gemma-v0.1",
    device_map="auto",
    torch_dtype=torch.bfloat16,
)

def extractConcepts(prompt: str, metadata):
    SYS_PROMPT = (
        "Your task is extract the key concepts (and non personal entities) mentioned in the given context. "
        "Extract only the most important and atomistic concepts, if  needed break the concepts down to the simpler concepts."
        "Categorize the concepts in one of the following categories: "
        "[event, concept, place, object, document, organisation, condition, misc]\n"
        "Format your output as a list of json with the following format:\n"
        "[\n"
        "   {\n"
        '       "entity": The Concept,\n'
        '       "importance": The concontextual importance of the concept on a scale of 1 to 5 (5 being the highest),\n'
        '       "category": The Type of Concept,\n'
        "   }, \n"
        "{ }, \n"
        "]\n"
        "only output the json, include no notes or introductory statements"
        "The entire output should be readable by a program that can interpret json"
    )
    bprompt="Using this: "+prompt+"/n"+SYS_PROMPT
    messages = [
    {
        "role": "system",
        "content": "",  # Model not yet trained for follow this
    },
    {"role": "user", "content": bprompt},
    ]
    outputs = pipe(
    messages,
    max_new_tokens=128,
    do_sample=True,
    temperature=0.7,
    top_k=50,
    top_p=0.95,
    stop_sequence="<|im_end|>",
    )
    response=outputs[0]["generated_text"][-1]["content"]
    try:
        result = json.loads(response)
        result = [dict(item, **metadata) for item in result]
    except:
        print("\n\nERROR ### Here is the buggy response: ", response, "\n\n")
        result = None
    return result


def graphPrompt(input: str, metadata:{}):
    print("hello")

    SYS_PROMPT = (
        "You are a network graph maker who extracts terms and their relations from a given context. "
        "You are provided with a context chunk (delimited by ```) Your task is to extract the ontology "
        "of terms mentioned in the given context. These terms should represent the key concepts as per the context. \n"
        "Thought 1: While traversing through each sentence, Think about the key terms mentioned in it.\n"
            "\tTerms may include object, entity, location, organization, person, \n"
            "\tcondition, acronym, documents, service, concept, etc.\n"
            "\tTerms should be as atomistic as possible\n\n"
        "Thought 2: Think about how these terms can have one on one relation with other terms.\n"
            "\tTerms that are mentioned in the same sentence or the same paragraph are typically related to each other.\n"
            "\tTerms can be related to many other terms\n\n"
        "Thought 3: Find out the relation between each such related pair of terms. \n\n"
        "Format your output as a list of json. Each element of the list contains a pair of terms"
        "and the relation between them, like the follwing: \n"
        "[\n"
        "   {\n"
        '       "node_1": "A concept from extracted ontology",\n'
        '       "node_2": "A related concept from extracted ontology",\n'
        '       "edge": "relationship between the two concepts, node_1 and node_2 in one or two sentences"\n'
        "   }, {...}\n"
        "]"
        "try to keep the edges consise, but do not sacrifice relavent information"
        "only output the json, include no notes or introductory statements"
        "The entire output should be readable by a program that can interpret json"
    )

    USER_PROMPT = f"context: ```{input}``` \n\n output: "
    bprompt="Using this: "+USER_PROMPT+"/n"+SYS_PROMPT
    messages = [
    {
        "role": "system",
        "content": "",  # Model not yet trained for follow this
    },
    {"role": "user", "content": bprompt},
    ]
    outputs = pipe(
    messages,
    max_new_tokens=512,
    do_sample=True,
    temperature=0.7,
    top_k=50,
    top_p=0.95,
    stop_sequence="<|im_end|>",
    )
    out=outputs[0]["generated_text"][-1]["content"]
    response="[\n"+out.split("[\n")[1].split("]")[0]+"]"
    try:
        result = json.loads(response)
        result = [dict(item, **metadata) for item in result]
    except:
        print("\n\nERROR ### Here is the buggy response: ", response, "\n\n")
        result = None
    return result
