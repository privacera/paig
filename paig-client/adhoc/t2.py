from langchain.llms.fake import FakeListLLM

llm = FakeListLLM(responses=["a", "b", "c"])
for i in range(10):
    print(llm("prompt1"))
