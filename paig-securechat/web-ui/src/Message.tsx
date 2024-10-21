import AccountCircleIcon from "@mui/icons-material/AccountCircle";
import ContentCopyOutlinedIcon from "@mui/icons-material/ContentCopyOutlined";
import DoneOutlinedIcon from "@mui/icons-material/DoneOutlined";
import { Box, IconButton, SxProps, Typography, Table, TableBody, TableCell, TableHead, TableRow } from "@mui/material";
import React from "react";
import { Logo } from "./icons";
import { useSnackbar } from "notistack";
import MarkdownComponent from "./components/MarkdownComponent";
import CancelIcon from "@mui/icons-material/Cancel";

const Message = ({
  me,
  msg,
  index,
  removeThatChat,
  sourceMetadata
}: {
  me: boolean;
  msg: string;
  index?: number;
  removeThatChat?: (index: number) => void;
  sourceMetadata: any;
}) => {
  const { enqueueSnackbar } = useSnackbar();
  const [isCopied, setIsCopied] = React.useState(false);

    // Parse the string of sourceMetadata into a JSON object (list of dictionaries)
  let parsedMetadata: any[] = [];
  try {
    parsedMetadata = JSON.parse(sourceMetadata.replace(/'/g, '"')); // Replace single quotes with double quotes to make it valid JSON
  } catch (error) {
    console.error("Failed to parse sourceMetadata", error);
  }

  // Generate a Material-UI table from the parsed metadata
  const generateMaterialUITable = (data: any[]) => {
    if (!data || data.length === 0) return null;

    const headers = Object.keys(data[0]);

    return (
      <div className="chat-source-metadata">
        <Typography id="source-metadata-typography" gutterBottom align="left">
        Metadata:
        </Typography>
      <Table sx={{width: '100%' }} size="small">
        <TableHead>
          <TableRow>
            {headers.map(header => (
              <TableCell key={header} style={{ fontWeight: 'bold' }}>
                {header}
              </TableCell>
            ))}
          </TableRow>
        </TableHead>
        <TableBody>
          {data.map((item, rowIndex) => (
            <TableRow key={rowIndex}>
              {headers.map(header => (
                <TableCell key={header}>
                {Array.isArray(item[header])
                  ? item[header].join(", ")
                  : typeof item[header] === 'object' && item[header] !== null
                  ? JSON.stringify(item[header], null, 2) // Convert object to pretty JSON
                  : item[header]?.toString() || ""}
              </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
        </div>
    );
  };

  const markdownTable = generateMaterialUITable(parsedMetadata);

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
          {/* Render the message */}
          <Typography>{msg.trim()}</Typography>

          {/* Render the Material-UI table */}
          {markdownTable}
        </Box>
      </Box>
    </Box>
  );
};

export default Message;
