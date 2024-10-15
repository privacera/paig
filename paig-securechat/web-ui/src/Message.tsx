import AccountCircleIcon from "@mui/icons-material/AccountCircle";
import ContentCopyOutlinedIcon from "@mui/icons-material/ContentCopyOutlined";
import DoneOutlinedIcon from "@mui/icons-material/DoneOutlined";
import { Box, IconButton, SxProps, Typography } from "@mui/material";
import React from "react";
import { Logo } from "./icons";
import { useSnackbar } from "notistack";
import MarkdownComponent from "./components/MarkdownComponent";
import CancelIcon from "@mui/icons-material/Cancel";

const Message = ({
  me,
  msg,
  index,
  removeThatChat
}: {
  me: boolean;
  msg: string;
  index?: number;
  removeThatChat?: (index: number) => void;
}) => {
  const { enqueueSnackbar } = useSnackbar();
  const [isCopied, setIsCopied] = React.useState(false);

  const copyToClipboard = () => {
    if (!navigator.clipboard || !navigator.clipboard.writeText) {
      enqueueSnackbar("Copy to clipboard failed", {
        variant: "warning",
        autoHideDuration: 1500
      });
      return;
    }

    navigator.clipboard.writeText(msg).then(() => {
      enqueueSnackbar("Copied to clipboard", {
        variant: "info",
        autoHideDuration: 1500
      });
      setIsCopied(true);

      setTimeout(() => {
        setIsCopied(false);
      }, 2000);
    });
  };

  const messageContentStyle: SxProps = {
    paddingLeft: "5px",
    paddingRight: "32px",
    color: me ? "text.secondary" : "text.primary",
    fontSize: "16px",
    lineHeight: "22px",
    width: "100%",
    whiteSpace: "pre-line"
  };

  return (
    <Box
      id="promptResponse"
      sx={{
        display: "flex",
        flexDirection: me ? "row-reverse" : "row"
      }}
    >
      <Box
        sx={{
          paddingTop: "16px",
          paddingRight: me ? "0" : "8px",
          paddingLeft: me ? "8px" : "0"
        }}
      >
        {me ? <AccountCircleIcon /> : <Logo />}
      </Box>
      <Box
        sx={{
          display: "flex",
          width: "100%",
          flexDirection: "column",
          position: "relative"
        }}
      >
        <Box
          id="clipboard"
          sx={{
            position: "absolute",
            right: "0",
            top: "8px"
          }}
        >
          <IconButton
            onClick={copyToClipboard}
            sx={{
              ml: "auto"
            }}
          >
            {isCopied ? <DoneOutlinedIcon /> : <ContentCopyOutlinedIcon />}
          </IconButton>
        </Box>
        <Box id="chat_msg" sx={messageContentStyle}>
          {me ? (
            <Typography>{msg.trim()}</Typography>
          ) : (
            <MarkdownComponent content={msg.trim()} />
          )}
        </Box>
      </Box>
    </Box>
  );
};

export default Message;
