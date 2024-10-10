import fetchData from "./index";
import { SECURECHAT_BASE_ROUTE } from "../utils";

export const postAskQuestionApi = (chatId: string | undefined, data: any) => {
  const url: string =  `${SECURECHAT_BASE_ROUTE}/conversations/${chatId}/prompt`;
  return fetchData({
    url,
    method: "post",
    data
  });
};

export const postCreateConversation = (data: any, user_id:  any) => {
  const url: string =  `${SECURECHAT_BASE_ROUTE}/conversations/prompt`;
  return fetchData({
    url,
    method: "post",
    data
  });
}

export const getAllConversationsApi = (data: any) => {
  const url: string = `${SECURECHAT_BASE_ROUTE}/conversations`;
  return fetchData({
    url,
    method: "get"
  });
};

export const getAllAIApplicationsApi = () => {
  const url: string = `${SECURECHAT_BASE_ROUTE}/ai_applications`;
  return fetchData({
    url,
    method: "get"
  });
};

export const getConversationWithIdApi = (chatId: string | undefined) => {
  const url: string = `${SECURECHAT_BASE_ROUTE}/conversations/${chatId}`;
  return fetchData({
    url,
    method: "get"
  });
};

export const putConversationIdApi = (id: any) => {
  const url: string = `${SECURECHAT_BASE_ROUTE}/conversation/${id}`;
  return fetchData({
    url,
    method: "put"
  });
};

export const postConversationApi = (data: any) => {
  const url: string = `${SECURECHAT_BASE_ROUTE}/conversation`;
  return fetchData({
    url,
    method: "post",
    data
  });
};

export const postLoginApi = (data: any, authToken: any = null) => {
  const url: string = `${SECURECHAT_BASE_ROUTE}/user/login`;
  if (authToken) {
    return fetchData({
      url,
      method: "post",
      data,
      headers: {"Authorization" : `Bearer ${authToken}`}
    });
  } else {
    return fetchData({
      url,
      method: "post",
      data
    });
  }
};

export const postSignupApi = (data: any) => {
  const url: string = `${SECURECHAT_BASE_ROUTE}/auth/signup`;
  return fetchData({
    url,
    method: "post",
    data
  });
};

export const getServerConfig = () => {
  const url: string = `${SECURECHAT_BASE_ROUTE}/server/config`;
  return fetchData({
    url,
    method: "get"
  });
};
