import inspect
import json
import time

import langchain.llms


# show all the attributes of langchain.llms
#print(dir(langchain.llms))
#print(langchain.llms.get_type_to_cls_dict())

#methods_to_intercept1 = ["_call"]
skip_classes = ["LLM", "BaseLLM", "BaseLanguageModel", "Serializable", "RunnableSerializable", "BaseModel", "Representation", "ABC", "object"]
methods_to_intercept = ["_generate", "_agenerate", "_stream", "_astream", "_call"]
#methods_to_intercept = ["_call"]

list_of_methods_to_intercept = []
def show_methods_for_class(cls):
    cls_methods = dict()
    for method_name, method in inspect.getmembers(cls, callable):
        if method_name.startswith("__"):
            continue
        # if method_name == "_call":
        #print(f"method_name: {method_name}, method: {method}, method.__class__: {method.__class__}, method.__qualname__: {method.__qualname__}")
        qual_name = method.__qualname__
        key = qual_name.split(".")[0]
        #if key == cls.__name__:
        if key not in cls_methods:
            cls_methods[key] = []
        cls_methods[key].append(method_name)

    for c in inspect.getmro(cls):
        if c.__name__ in skip_classes:
            continue
        print(f"\nbase-class__name__: {c.__name__}, base-class.__module__: {c.__module__} of {cls.__name__}")
        if c.__name__ in cls_methods:
            print(json.dumps(cls_methods[c.__name__], indent=4))
            for m_name in cls_methods[c.__name__]:
                if m_name in methods_to_intercept:
                    to_intercept = (c.__module__, c.__name__, m_name)
                    if to_intercept not in list_of_methods_to_intercept:
                        list_of_methods_to_intercept.append(to_intercept)
                        print(f"will intercept {to_intercept} for class {cls.__name__}")
        else:
            print(f"No methods found for this base-class: {c.__name__}")

    print("-" * 80)

start_time = time.perf_counter()
start_time1 = time.time_ns()
for type_str, get_class_method in langchain.llms.get_type_to_cls_dict().items():
    print(f"Type: {type_str}")
    cls = get_class_method()
    # print(f"cls={cls}, mro: {inspect.getmro(cls)}")
    # for c in inspect.getmro(cls):
    #     print(f"base-class.__name__: {c.__name__}, base-class.__qualname__: {c.__qualname__}, base-class.__module__: {c.__module__}")
    show_methods_for_class(get_class_method())
end_time = time.perf_counter()
end_time1 = time.time_ns()


print("final list of methods to intercept:\n")
for x in list_of_methods_to_intercept:
    print(x)

print(f"total={len(list_of_methods_to_intercept)}")
print(f"total time taken: {end_time - start_time} seconds or {(end_time1 - start_time1)/1000/1000/1000} seconds")