import AddIcon from "@mui/icons-material/Add";
import MessageOutlinedIcon from "@mui/icons-material/MessageOutlined";
import {
  Divider,
  Grid,
  IconButton,
  ListItem,
  Menu,
  MenuItem,
  Tooltip,
  Typography,
  useTheme
} from "@mui/material";
import Box from "@mui/material/Box";
import Drawer from "@mui/material/Drawer";
import List from "@mui/material/List";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import { useSnackbar } from "notistack";
import React, { useContext, useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import DataContext from "../context/DataContext";
import InputChat from "./InputChat";
import { DRAWERWIDTH, NAVBARHEIGHT } from "../constants";
import {
  postAskQuestionApi,
  getAllConversationsApi,
  getAllAIApplicationsApi,
  postCreateConversation
} from "../Api/apis";
import { DotLoader } from "../components/Loader";
import DeleteIcon from "@mui/icons-material/Delete";
import CloseIcon from "@mui/icons-material/Close";
import CheckIcon from "@mui/icons-material/Check";

const PageLayout = ({
  children
}: {
  children: React.ReactNode;
}): React.ReactElement => {
  const theme = useTheme();
  const navigate = useNavigate();
  const location = useLocation();

  const { enqueueSnackbar } = useSnackbar();

  const userData = useContext(DataContext)?.userData;

  const conversations = useContext(DataContext)?.conversations;
  const setConversations = useContext(DataContext)?.setConversations;
  const setCurrentConversation =
    useContext(DataContext)?.setCurrentConversation;
  const currentConversation = useContext(DataContext)?.currentConversation;
  const appendReplyToPrompt = useContext(DataContext)?.appendReplyToPrompt;
  const appendPrompt = useContext(DataContext)?.appendPrompt;
  const appendConversation = useContext(DataContext)?.appendConversation;
  const postToServer = useContext(DataContext)?.postToServer;
  const AIApplicationData = useContext(DataContext)?.AIApplicationData;
  const setAIApplicationData = useContext(DataContext)?.setAIApplicationData;

  const selectedAIApplicationObj = useContext(DataContext)?.selectedAIApplicationObj;
  const setselectedAIApplicationObj = useContext(DataContext)?.setselectedAIApplicationObj;

  const setAIApplicationMap = useContext(DataContext)?.setAIApplicationMap;

  const [loading, setLoading] = useState(false);
  const [anchorEl, setAnchorEl] = React.useState<HTMLElement | null>(null);
  const redirect = useContext(DataContext)?.redirect;
  const currentAIApplication = useContext(DataContext)?.currentAIApplication;
  const setCurrentAIApplication = useContext(DataContext)?.setCurrentAIApplication;
  const setInput = useContext(DataContext)?.setInput;
  const setConversationLoader = useContext(DataContext)?.setConversationLoader;
  const conversationLoader = useContext(DataContext)?.conversationLoader;
  const setAllConverstionLoader =
    useContext(DataContext)?.setAllConverstionLoader;
  const allConverstionLoader = useContext(DataContext)?.allConverstionLoader;
  const setChatLoader = useContext(DataContext)?.setChatLoader;
  const setFirstConversation = useContext(DataContext)?.setFirstConversation;
  const [deleteBtnState, setDeleteBtnState] = useState(false);

  const handleMenuOpen = (event: any) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleInput = async (message: string, temperature: number) => {
    if (userData && appendPrompt) {
      setLoading(true);
      if (currentConversation === null && setCurrentConversation) {
        let newConversationData = {
          conversation_uuid: 'new_conversation',
          messages: [],
          title: "New Conversation",
          ai_application_name: selectedAIApplicationObj?.name
        }
        setConversations && setConversations((prevCon) => {
          if (prevCon) {
            return [newConversationData, ...prevCon];
          } else return prevCon;
        });
        setCurrentConversation(newConversationData);
        appendPrompt(message);
      } else {
        appendPrompt(message);
      }
      if (currentConversation == null) {
        navigate(`/chat/new`);
        setFirstConversation &&
          setFirstConversation({
            AIApplication: currentAIApplication || "General",
            question: message,
            loader: true
          });
      }
      let params = {
        prompt: message,
        // temperature: temperature,
        user_id: userData.user_id,
        conversation_uuid: currentConversation?.conversation_uuid,
        ai_application_name: currentAIApplication
      };
      let createConversationParams = {
        prompt: message,
        ai_application_name: currentAIApplication
      }
      try {
        if (currentConversation?.conversation_uuid) {
          const resp = await postAskQuestionApi(currentConversation?.conversation_uuid, params);
          setLoading(false);
          appendReplyToPrompt && appendReplyToPrompt(resp.data, false);
          setChatLoader && setChatLoader(false);
        } else {
          const resp = await postCreateConversation(createConversationParams, userData.user_id);
          setLoading(false);
          appendConversation && appendConversation(resp.data);
          setCurrentConversation && setCurrentConversation(resp.data);
          navigate(`/chat/c/${resp.data.conversation_uuid}`);
          setChatLoader && setChatLoader(false);
        }
      } catch (err: any) {
        setLoading(false);
        setChatLoader && setChatLoader(false);
        enqueueSnackbar(err.message, {
          variant: "error"
        });
      }
    }
  };

  useEffect(() => {
    if (!userData) {
      navigate("/login");
    } else {
      getAllConversations();
    }
  }, [userData, setConversations]);

  useEffect(() => {
    getAllAIApplications();
  }, []);

  useEffect(() => {
    setdefaultAIApplication();
  }, [AIApplicationData]);

  useEffect(() => {
    if (redirect && typeof redirect === "number") {
      navigate(`c/${redirect}`);
    }
  }, [redirect]);

  useEffect(() => {
    console.log(currentConversation);
  }, [currentConversation]);

  const setdefaultAIApplication = () => {
    if (AIApplicationData) {
      const defaultAIApplication = AIApplicationData.filter((item) => item.default);
      setselectedAIApplicationObj && setselectedAIApplicationObj(defaultAIApplication[0]);
      defaultAIApplication &&
        defaultAIApplication[0] &&
        setCurrentAIApplication &&
        setCurrentAIApplication(defaultAIApplication[0].name);
    }
  };

  const getAllConversations = async () => {
    if (userData) {
      try {
        const res = await getAllConversationsApi({
          user_id: userData.user_id
        });
        setConversations && setConversations(res.data.items);
        setAllConverstionLoader && setAllConverstionLoader(false);
      } catch (err: any) {
        enqueueSnackbar(err.message, {
          variant: "error"
        });
        setAllConverstionLoader && setAllConverstionLoader(false);
      }
    }
  };

  const getAllAIApplications = async () => {
    if (userData) {
      try {
        const res = await getAllAIApplicationsApi();
        setAIApplicationData && setAIApplicationData(res.data.AI_applications);
        makeAIApplicationMap(res.data.AI_applications);
      } catch (err: any) {
        enqueueSnackbar(err.message, {
          variant: "error"
        });
      }
    }
  };

  const makeAIApplicationMap = (AIApplicationData: any) => {
    let AIApplicationMap: { [key: string]: string } = {};
    for (const data of AIApplicationData) {
      AIApplicationMap[data.name] = data.display_name;
    }
    setAIApplicationMap && setAIApplicationMap(AIApplicationMap);
  };

  const startNewChat = (viewObject: any) => {
    setCurrentConversation && setCurrentConversation(null);
    navigate("/chat");

    setselectedAIApplicationObj && setselectedAIApplicationObj(viewObject);
    setCurrentAIApplication && setCurrentAIApplication(viewObject.name);
    setAnchorEl(null);
  };

  const handleCardClick = (title: string, text: string) => {
    if (title == "Sample questions...") {
      setInput && setInput(text);
    }
    return;
  };

  const handleDeleteConversation = () => {
    // Add delete api here

    navigate(`/chat`);
    setCurrentConversation && setCurrentConversation(null);
    setdefaultAIApplication();
    setDeleteBtnState(false);
  };
  type Conversation = {
    conversation_uuid: string | null;
    title: string;
    messages: Message[];
    ai_application_name?: string;
    AIApplication?: string;
  };

  const handleListBtnClick = (data: Conversation) => {
    location.pathname !== `/chat/c/${data.conversation_uuid}` &&
      setConversationLoader &&
      setConversationLoader(true);
    navigate(`/chat/c/${data.conversation_uuid}`);
    setDeleteBtnState(false);
  };

  return (
    <Box sx={{ display: "flex", flexDirection: "row" }}>
      <Box
        component="main"
        sx={{ flexGrow: 1, bgcolor: "background.secondary" }}
      >
        <Divider />
        <Grid container>
          <Grid item xs={2}>
            <Drawer
              variant="permanent"
              sx={{
                // width: DRAWERWIDTH,
                flexShrink: 0,
                boxSizing: "border-box",
                borderRight: 0,
                [`& .MuiDrawer-paper`]: {
                  top: `${NAVBARHEIGHT + 1}px`
                }
              }}
            >
              <Box
                component="nav"
                sx={{ flexShrink: { md: 0 }, width: DRAWERWIDTH, mb: 5 }}
              >
                {allConverstionLoader ? (
                  <DotLoader />
                ) : (
                  <List sx={{ paddingTop: "0", paddingBottom: "30px" }}>
                    <div>
                      <ListItemButton
                        id="newConversationBtn"
                        sx={{
                          alignItems: "flex-start",
                          fontSize: "14px",
                          height: "46px"
                        }}
                        onClick={handleMenuOpen}
                        key={`new_conversation_test_sidebar`}
                        selected={location.pathname === `/chat`}
                      >
                        <ListItemIcon
                          sx={{ my: "auto", minWidth: "20px", mr: 1 }}
                        >
                          {<AddIcon fontSize="small" />}
                        </ListItemIcon>
                        <ListItemText
                          primary={
                            <Typography
                              fontSize={"inherit"}
                            >{`New Conversation`}</Typography>
                          }
                        />
                      </ListItemButton>
                      <Menu
                        id="hover-menu"
                        anchorEl={anchorEl}
                        open={Boolean(anchorEl)}
                        onClose={handleMenuClose}
                      >
                        {AIApplicationData &&
                          AIApplicationData
                            ?.filter((AIApplication: any) => AIApplication.enable)
                            ?.map((AIApplication: any) => (
                              <MenuItem onClick={() => startNewChat(AIApplication)}>
                                {AIApplication.display_name}
                              </MenuItem>
                            ))}
                      </Menu>
                    </div>
                    {conversations &&
                      conversations.map((data) => (
                        <ListItem
                          id="conversations"
                          sx={{ p: 0 }}
                          key={data.conversation_uuid}
                          secondaryAction={
                            location.pathname ===
                              `/chat/c/${data.conversation_uuid}` &&
                            (deleteBtnState ? (
                              <>
                                <IconButton onClick={handleDeleteConversation}>
                                  <CheckIcon fontSize="small" />
                                </IconButton>
                                <IconButton
                                  edge="end"
                                  onClick={() => setDeleteBtnState(false)}
                                >
                                  <CloseIcon fontSize="small" />
                                </IconButton>
                              </>
                            ) : (
                              <Tooltip
                                title="Delete Conversation"
                                arrow
                                placement="top"
                              >
                                <IconButton
                                  onClick={() => setDeleteBtnState(true)}
                                  edge="end"
                                >
                                  <DeleteIcon fontSize="small" />
                                </IconButton>
                              </Tooltip>
                            ))
                          }
                        >
                          <ListItemButton
                            sx={{
                              alignItems: "flex-start",
                              fontSize: "14px",
                              height: "46px",
                              ...(location.pathname ===
                                `/chat/c/${data.conversation_uuid}` &&
                                deleteBtnState && {
                                  ".MuiTypography-root": {
                                    width: "140px"
                                  }
                                })
                            }}
                            onClick={() => handleListBtnClick(data)}
                            data-testid={`${data.conversation_uuid}_test_sidebar`}
                            key={data.conversation_uuid}
                            selected={
                              location.pathname ===
                              `/chat/c/${data.conversation_uuid}`
                            }
                          >
                            <ListItemIcon
                              sx={{ my: "auto", minWidth: "20px", mr: 1 }}
                            >
                              <MessageOutlinedIcon fontSize="small" />
                            </ListItemIcon>
                            <ListItemText
                              primary={
                                <Typography
                                  fontSize={"inherit"}
                                  sx={{
                                    whiteSpace: "nowrap",
                                    overflow: "hidden",
                                    textOverflow: "ellipsis"
                                  }}
                                >
                                  {location.pathname ===
                                    `/chat/c/${data.conversation_uuid}` &&
                                  deleteBtnState
                                    ? `Delete "${data.title}"`
                                    : data.title}
                                </Typography>
                              }
                            />
                          </ListItemButton>
                        </ListItem>
                      ))}
                  </List>
                )}
              </Box>
            </Drawer>
          </Grid>
          <Grid item xs={8}>
            <Box
              sx={{
                flexGrow: 1,
                minHeight: `calc(100vh - 97px)`,
                WebkitFlexGrow: 1,
                msFlex: 1,
                // my: `${DRAWERWIDTH}px`,
                display: "flex",
                position: "relative",
                flexDirection: "column",
                mt: 4
              }}
              className="main-box"
            >
              <Box
                sx={{
                  position: "relative",
                  maxHeight: `calc(100vh - 215px)`,
                  overflowY: "auto",
                  pb: 2,
                  minHeight: "100px"
                }}
                id="chat_box_container"
              >
                {children}
              </Box>
              <Box
                id="input_container"
                zIndex={100}
                sx={{
                  mx: "auto",
                  width: "100%",
                  position: "fixed",
                  bottom: 20,
                  left: "50%",
                  transform: "translateX(-50%)",
                  maxWidth: "900px",
                  px: 2
                }}
              >
                <InputChat chatLoading={loading} handleInput={handleInput} />
              </Box>
            </Box>
          </Grid>
          <Grid
            item
            xs={2}
            sx={{ background: location.pathname !== `/chat` ? "#F4F4F4" : "" }}
          >
            {conversationLoader ? (
              <DotLoader />
            ) : (
              <Box>
                {location.pathname !== `/chat` &&
                  selectedAIApplicationObj &&
                  selectedAIApplicationObj.welcome_column2 && (
                    <Box>
                      <List>
                        <ListItem>
                          <Typography variant="h6" component="p" mt={1}>
                            {selectedAIApplicationObj.welcome_column2.header}
                          </Typography>
                        </ListItem>
                        {selectedAIApplicationObj.welcome_column2.messages.map(
                          (text, index) => (
                            <>
                              <Divider />
                              <ListItemButton
                                onClick={() =>
                                  handleCardClick(
                                    selectedAIApplicationObj.welcome_column2.header,
                                    text
                                  )
                                }
                              >
                                {text}
                              </ListItemButton>
                            </>
                          )
                        )}
                      </List>
                    </Box>
                  )}
              </Box>
            )}
          </Grid>
        </Grid>
      </Box>
    </Box>
  );
};

const CARD_STYLE = {
  bgcolor: "secondary.paper",
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  justifyContent: "center",
  textAlign: "center"
};

export default PageLayout;
