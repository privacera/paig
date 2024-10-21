import { Box, Container, Paper } from "@mui/material";
import { useSnackbar } from "notistack";
import React, { useContext, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import Message from "../Message";
import DataContext from "../context/DataContext";
import { DotLoader } from "../components/Loader";
import { getConversationWithIdApi } from "../Api/apis";

const Chat = () => {
  const chatId: string | undefined = useParams().id;
  const setCurrentConversation =
    useContext(DataContext)?.setCurrentConversation;
  const currentConversation: Conversation | null | undefined =
    useContext(DataContext)?.currentConversation;
  const AIApplicationMap = useContext(DataContext)?.AIApplicationMap;

  const { enqueueSnackbar } = useSnackbar();
  const navigate = useNavigate();
  const postToServer = useContext(DataContext)?.postToServer;
  const setCurrentAIApplication = useContext(DataContext)?.setCurrentAIApplication;
  const setselectedAIApplicationObj = useContext(DataContext)?.setselectedAIApplicationObj;
  const AIApplicationData = useContext(DataContext)?.AIApplicationData;
  const conversationLoader = useContext(DataContext)?.conversationLoader;
  const setConversationLoader = useContext(DataContext)?.setConversationLoader;
  const chatLoader = useContext(DataContext)?.chatLoader;

  useEffect(() => {
    chatId !== "new" && getConversationWithId();
  }, [chatId]);

  const getConversationWithId = async () => {
    try {
      const res = await getConversationWithIdApi(chatId);
      setConversationLoader && setConversationLoader(false);
      if (res.data.messages) res.data.messages.reverse()
      setCurrentConversation && setCurrentConversation(res.data);
      setCurrentAIApplication && setCurrentAIApplication(res.data.ai_application_name);

      if (AIApplicationData) {
        const selectedAIApplication = AIApplicationData.filter(
          (item) => item.name === res.data.ai_application_name
        );
        setselectedAIApplicationObj && setselectedAIApplicationObj(selectedAIApplication[0]);
      }
    } catch (err) {
      setConversationLoader && setConversationLoader(false);
      enqueueSnackbar("Conversation not found", {
        variant: "error"
      });
      navigate("/chat");
    }
  };

  useEffect(updateScroll, [currentConversation]);

  function updateScroll() {
    const container = document.getElementById("chat_box_container");
    if (container) {
      container.scrollTo({
        top: container.scrollHeight,
        behavior: "smooth"
      });
    }
  }

  const removeThatChat = (index: number) => {
    if (!currentConversation) return;

    const newMessages = [...currentConversation.messages];
    newMessages.splice(index, 2);

    if (setCurrentConversation) {
      setCurrentConversation((prevConversation) => {
        if (!prevConversation) return null;

        return {
          ...prevConversation,
          messages: newMessages
        };
      });
    }
    postToServer && postToServer();

    enqueueSnackbar("Chat deleted", {
      variant: "error",
      autoHideDuration: 2 * 1000
    });
  };

  return (
    <>
      {conversationLoader ? (
        <DotLoader />
      ) : (
        <Box id="chat_container">
          <div
            id="ai_application_name"
            className="chat-title-sticky"
            style={{ fontWeight: 400, fontSize: 25 }}
          >
            {currentConversation &&
              currentConversation.ai_application_name &&
              AIApplicationMap &&
              AIApplicationMap[currentConversation.ai_application_name]}
          </div>
          <Container
            maxWidth="md"
            id="chats"
            sx={{
              display: "flex",
              height: "100%",
              flexDirection: "column",
              borderRadius: 2,
              py: 2
            }}
          >
            <Paper
              sx={{
                my: 1
              }}
              variant={"outlined"}
            >
              {currentConversation &&
                currentConversation.messages?.map(
                  (item: any, index: number) => (
                    <Box
                      id="message_box"
                      key={`${currentConversation.conversation_uuid}-${index}`}
                      className={item.type==="prompt" ? "chat-query" : "chat-response"}
                    >
                      <Message
                        msg={item.content}
                        me={item.type==="prompt" || false}
                        index={index}
                        removeThatChat={removeThatChat}
                        sourceMetadata={item.source_metadata}
                      />
                    </Box>
                  )
                )}
            </Paper>
            {chatLoader ? <DotLoader withpadding={false} /> : ""}
          </Container>
        </Box>
      )}
    </>
  );
};

const FirstPrompt = () => {
  const firstConversation = useContext(DataContext)?.firstConversation;
  const AIApplicationMap = useContext(DataContext)?.AIApplicationMap;

  return (
    <Box id="firstchat_container">
      <div
        className="chat-title-sticky"
        style={{ fontWeight: 400, fontSize: 25 }}
      >
        {firstConversation &&
          firstConversation.AIApplication &&
          AIApplicationMap &&
          AIApplicationMap[firstConversation.AIApplication]}
      </div>
      <Container
        maxWidth="md"
        id="chats"
        sx={{
          display: "flex",
          height: "100%",
          flexDirection: "column",
          borderRadius: 2,
          py: 2
        }}
      >
        <Paper
          sx={{
            my: 1
          }}
          variant={"outlined"}
        >
          <Box id="message_box" className="chat-query">
            <Message
              msg={(firstConversation && firstConversation.question) || ""}
              me={true}
              sourceMetadata={null}
            />
          </Box>
        </Paper>
        <DotLoader withpadding={false} />
      </Container>
    </Box>
  );
};

export default Chat;
export { FirstPrompt };
