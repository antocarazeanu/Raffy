from model77777 import user
from knowledge import vectorstore_dict

def agent_call(file_name):
    print("AICI" + user)
    file_name = file_name + ".docx"
    vectorstore = vectorstore_dict[file_name]
    
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    
    sources = retriever.get_relevant_documents(user)
    return sources