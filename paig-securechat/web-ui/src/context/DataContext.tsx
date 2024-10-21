import axios from "axios";
import PropTypes from "prop-types";
import React, {
  createContext,
  Dispatch,
  ReactNode,
  SetStateAction,
  useEffect,
  useState
} from "react";
import User from "../models/userModel";
import { decryptData, SECURECHAT_BASE_ROUTE } from "../utils";

interface DataContextModel {
  userData: User | null;
  conversations: Array<Conversation> | null;
  setConversations: Dispatch<SetStateAction<Array<Conversation> | null>>;
  currentConversation: Conversation | null;
  setCurrentConversation: Dispatch<SetStateAction<Conversation | null>>;
  handleAuth(value: User): void;
  handlelogout(): void;
  sessionCleanUp(): void;
  appendReplyToPrompt(message: string, user: boolean): void;
  appendConversation(data: any): void;
  appendPrompt(message: string): void;
  postToServer(): void;
  redirect: boolean | number;
  setRedirect: Dispatch<SetStateAction<boolean>>;
  isCurrentUserConversation: boolean;
  input: string;
  setInput: Dispatch<SetStateAction<string>>;
  AIApplicationData: AIApplication[] | null;
  setAIApplicationData: Dispatch<SetStateAction<Array<AIApplication> | null>>;
  selectedAIApplicationObj: AIApplication | null;
  setselectedAIApplicationObj: Dispatch<SetStateAction<AIApplication | null>>;
  AIApplicationMap: { [key: string]: string } | null | undefined;
  setAIApplicationMap: Dispatch<SetStateAction<{ [key: string]: string } | null>>;
  currentAIApplication: string | null;
  setCurrentAIApplication: Dispatch<SetStateAction<string | null>>;
  firstConversation: ConversationState;
  setFirstConversation: Dispatch<SetStateAction<ConversationState>>;
  //loaders
  conversationLoader: boolean;
  setConversationLoader: Dispatch<SetStateAction<boolean>>;
  chatLoader: boolean;
  setChatLoader: Dispatch<SetStateAction<boolean>>;
  allConverstionLoader: boolean;
  setAllConverstionLoader: Dispatch<SetStateAction<boolean>>;
  ServerConfig: any;
  setServerConfig: Dispatch<SetStateAction<{ [key: string]: string } | null>>;
  OktaAuthClient: any;
  setOktaAuthClient: Dispatch<SetStateAction<{ [key: string]: string } | object | null>>;
}

const DataContext = createContext<DataContextModel | null>(null);

type DataProviderProps = {
  children: ReactNode;
};

interface ConversationState {
  AIApplication: string | undefined;
  question: string;
  loader: boolean;
}

function DataProvider({ children }: DataProviderProps): React.ReactElement {
  const [userData, setUserData] = useState<User | null>(() => {
    const user = localStorage.getItem("auth");
    if (!user) return undefined;
    const decrepted = decryptData(user);
    if (!decrepted) return undefined;
    return JSON.parse(decrepted);
  });
  const [conversations, setConversations] =
    useState<Array<Conversation> | null>(null);
  const [currentConversation, setCurrentConversation] =
    useState<Conversation | null>(null);
  // Set if current conversation is this users
  const [isCurrentUserConversation, setIsCurrentUserConversation] =
    useState<boolean>(true);

  const [redirect, setRedirect] = useState<boolean>(false);
  const [input, setInput] = useState("");
  const [AIApplicationData, setAIApplicationData] = useState<Array<AIApplication> | null>(null);
  const [selectedAIApplicationObj, setselectedAIApplicationObj] = useState<AIApplication | null>(null);
  const [AIApplicationMap, setAIApplicationMap] = useState<{ [key: string]: string } | null>(
    null
  );

  const [ServerConfig, setServerConfig] = useState<{ [key: string]: string } | null>(
    null
  );
  const [OktaAuthClient, setOktaAuthClient] =  useState<{ [key: string]: string } | null | object>(
    null
  );
  const [currentAIApplication, setCurrentAIApplication] = useState<string | null>(null);

  const [conversationLoader, setConversationLoader] = useState<boolean>(true);
  const [chatLoader, setChatLoader] = useState<boolean>(false);
  const [allConverstionLoader, setAllConverstionLoader] =
    useState<boolean>(true);
  const [firstConversation, setFirstConversation] = useState<ConversationState>(
    { AIApplication: "", question: "", loader: false }
  );

  function handleAuth(value: User) {
    setConversations([]);
    setUserData(value);
  }
  function handlelogout() {
    sessionCleanUp();
    axios.post(`${SECURECHAT_BASE_ROUTE}/user/logout`, {})
    .then(function (response) {
      console.log(response);
    })
    .catch(function (error) {
      console.log(error);
    });
  }
  function sessionCleanUp() {
    setUserData(null);
    setRedirect(false);
    setConversations(null);
    localStorage.removeItem("auth");
  }
  useEffect(() => {
    if (currentConversation && currentConversation.conversation_uuid) {
      // Check if current conversation is in conversations
      const conversation = conversations?.find(
        (con) => con.conversation_uuid === currentConversation.conversation_uuid
      );
      if (conversation) {
        setIsCurrentUserConversation(true);
      } else {
        setIsCurrentUserConversation(false);
      }
    } else setIsCurrentUserConversation(true);
  }, [conversations, currentConversation]);

  function appendReplyToPrompt(message: any, user: boolean) {
    setCurrentConversation((prev) => {
      if (prev && message.length != 0) {
        let prompt: any = message.find((x: any) => x.type == 'prompt')
        let reply: any = message.find((x: any) => x.type == 'reply') 
        if (prompt || reply) {
          let appendList = []
          if (prompt) {
            prev.messages.pop()
            appendList.push(prompt)
          }
          if (reply) {
            appendList.push(reply)
          }
          return {
            ...prev,
            messages: [
              ...prev.messages,
              ... appendList
            ]
          };
        }
        return prev
      } else return prev;
    });
  }

  function appendPrompt(message: string) {
    setCurrentConversation((prev) => {
      if (prev) {
        return {
          ...prev,
          messages: [
            ...prev.messages,
            {
              content: message,
              created_on: new Date().toISOString(),
              prompt_id: null,
              type: 'prompt',
              message_uuid: null,
              source_metadata: null
            }
          ]
        };
      } else return prev;
    });
  }

  function appendConversation(data: any) {
    setConversations((prevCon) => {
      if (prevCon) {
        prevCon.shift()
        return [data, ...prevCon];
      } else return prevCon;
    });
  }

  function postToServer() {
    setCurrentConversation((prev) => {
      if (prev) {
        if (prev.conversation_uuid) {
          axios.put(`${SECURECHAT_BASE_ROUTE}/conversation/${prev.conversation_uuid}`, {
            messages: prev.messages
          });
        } else {
          axios
            .post(`${SECURECHAT_BASE_ROUTE}/conversation`, {
              user_id: userData?.user_id,
              messages: prev.messages,
              title: prev.title,
              ai_application_name: prev.ai_application_name
            })
            .then((res) => {
              setRedirect(res.data.conversation_uuid);
              setConversations((prevCon) => {
                if (prevCon) {
                  return [{ ...res.data, title: res.data.title }, ...prevCon];
                } else return prevCon;
              });
            });
        }
      }
      return prev;
    });
    setChatLoader(false);
  }

  return (
    <DataContext.Provider
      value={{
        userData,
        conversations,
        setConversations,
        currentConversation,
        setCurrentConversation,
        handleAuth,
        handlelogout,
        sessionCleanUp,
        appendReplyToPrompt,
        appendConversation,
        appendPrompt,
        postToServer,
        redirect,
        setRedirect,
        isCurrentUserConversation,
        input,
        setInput,
        AIApplicationData,
        setAIApplicationData,
        selectedAIApplicationObj,
        setselectedAIApplicationObj,
        AIApplicationMap,
        setAIApplicationMap,
        currentAIApplication,
        setCurrentAIApplication,
        conversationLoader,
        setConversationLoader,
        chatLoader,
        setChatLoader,
        allConverstionLoader,
        setAllConverstionLoader,
        firstConversation,
        setFirstConversation,
        setServerConfig,
        ServerConfig,
        setOktaAuthClient,
        OktaAuthClient
      }}
    >
      {children}
    </DataContext.Provider>
  );
}

DataProvider.propTypes = {
  children: PropTypes.node.isRequired
};

const DataConsumer = DataContext.Consumer;

export { DataProvider, DataConsumer };
export default DataContext;
