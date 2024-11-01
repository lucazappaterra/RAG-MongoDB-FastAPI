def create_template():
    template = """
        Answer the question based only on the following context:

        {context}
        
        If asked for previous interactions, you need to answer based on the following history:
        
        {history}
        
        Question: {question}
    """
    return template