import logging
import os,boto3,ai21
from typing import Any
import pickle as pkl
"""setting up the AWS Region"""
os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'
def query_endpoint(text, endpoint_name):
    response = ai21.Summarize.execute(
                          source=text,
                          sourceType="TEXT",
                          destination=ai21.SageMakerDestination(endpoint_name))
    logging.info("model predictions :: "+str(response.summary))
    return str(response.summary).replace(","," ").replace("\n",".").replace('"','')

def get_text_from_s3(s3_file_path):

    s3_client = boto3.client('s3')
    s3_path_list = s3_file_path.split("/")
    s3_response = s3_client.get_object(
        Bucket=s3_path_list[2],
        Key="/".join(s3_path_list[3:])
    )
    s3_object_body = s3_response.get('Body')
    return s3_object_body.read().decode()
    
    
def model_fn(model_dir: str) :
    try:
        with open(os.path.join(model_dir, "model.pickle.dat"), "rb") as f:
            booster = pkl.load(f)
        return booster
    except Exception:
        logging.exception("Failed to load model from checkpoint")
        raise

def input_fn(request_body: Any, content_type: str):

    if content_type == "text/csv":
        try:
            logging.info("Raw Data :: " + str(request_body))           
            input_list = str(request_body).strip().split('\n')
            logging.info("Number of rows Sent by Aurora :: " + str(len(input_list)))
            logging.info("Rows Sent by Aurora :: " + str(input_list))
            output_data = []
            for each_data in input_list:
                columns_data = []
                for splitted_data in each_data.split(","):
                    if splitted_data.strip().startswith("s3://") and splitted_data.endswith(".txt"):
                        columns_data.append(str(get_text_from_s3(s3_link)))                        
                    else:
                        columns_data.append(splitted_data)
                output_data.append(query_endpoint(", ".join(columns_data),"summarize"))                    
            return output_data
        except Exception:
            logging.exception("Failed to process input")
            raise
    raise ValueError('{{"error": "unsupported content type {}"}}'.format(content_type or "unknown"))


def predict_fn(output_data, model):  
    return output_data


def output_fn(output_data, accept):
    logging.info("Final output :: " + str("\n".join(output_data)).strip())
    return  str("\n".join(output_data)).strip()