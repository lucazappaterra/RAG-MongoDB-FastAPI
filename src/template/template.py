def create_template(user_id = None):
    if user_id is None:
        template = """
            Answer the question based only on the following context:

            {context}
            
            If asked for previous interactions, you need to answer based on the following history:
            
            {history}
            
            Question: {question}
        """
    else:
        template = """
            Answer the question at the end of this message, based only on the following context:

            {context}
            
            If asked for previous interactions, you need to answer based on the following history:
            
            {history}

            You are talking with {user_id}, greet him if there are no previous interactions in the provided history.
            
            Question: {question}
        """
    return template