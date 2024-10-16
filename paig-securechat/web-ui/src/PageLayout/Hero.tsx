import {
  Grid,
  Typography,
  Box,
  Paper,
  Container,
  useTheme
} from "@mui/material";
import React, { useContext, useEffect } from "react";
import { Sun, Thunder, Alert } from "../icons";

import "./../App.scss";
import DataContext from "../context/DataContext";
import { styled } from "@mui/system";
import { blue, grey } from "@mui/material/colors";
import { Theme } from "@mui/material/styles";
import { useSearchParams } from "react-router-dom";
import { StyledPaper } from "../components/StyledComponents";

const INFO_CARDS = [
  {
    id: 1,
    icon: <Sun />,
    title: "Examples",
    content: [
      "Explain quantum computing in simple terms",
      "Got any creative ideas for a 10 year old's birthday?",
      "How do I make an HTTP request in Javascript?"
    ]
  },
  {
    id: 2,
    icon: <Thunder />,
    title: "Capabilities",
    content: [
      "Remembers what user said earlier in the conversation",
      "Allows user to provide follow-up corrections",
      "Trained to decline inappropriate requests"
    ]
  },
  {
    id: 3,
    icon: <Alert />,
    title: "Limitations",
    content: [
      "May occasionally generate incorrect information",
      "May occasionally produce harmful instructions or biased content",
      "Limited knowledge of world and events after 2021"
    ]
  }
];

const CARD_STYLE = {
  bgcolor: "secondary.paper",
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  justifyContent: "center",
  textAlign: "center"
};

const INFO_CARD_STYLE = {
  mt: 2,
  fontSize: 14,
  lineHeight: 1.5,
  padding: 2
};

const Hero = () => {
  const theme = useTheme();
  const setInput = useContext(DataContext)?.setInput;
  const selectedAIApplicationObj = useContext(DataContext)?.selectedAIApplicationObj;
  const setConversationLoader = useContext(DataContext)?.setConversationLoader;
  const setCurrentConversation = useContext(DataContext)?.setCurrentConversation;

  useEffect(() => {
    setCurrentConversation && setCurrentConversation(null);
    setConversationLoader && setConversationLoader(false);
  }, []);

  const handleCardClick = (title: string, text: string) => {
    if (title == "Sample questions...") {
      setInput && setInput(text);
    }
    return;
  };

  return (
    <Container
      maxWidth="md"
      id="hero_container"
      sx={{
        display: "flex",
        height: "100%",
        flexDirection: "column"
      }}
    >
      <Grid container alignItems="center">
        <Grid item xs={12}>
          <Typography
            id="heroAIApplicationName"
            variant="h4"
            component="h1"
            align="center"
            mb={2}
          >
            PAIG SecureChat: {selectedAIApplicationObj?.display_name}
          </Typography>
        </Grid>
        <Grid container justifyContent="center" spacing={6}>
          {/* {INFO_CARDS.map(({ id, icon, title, content }) => (
            <Grid key={id} item md={12} lg={4}>
              <Box sx={CARD_STYLE}>
                {icon}
                <Typography variant="h6" component="p" mt={1}>
                  {title}
                </Typography>
                {content.map((text, index) => (
                  <StyledPaper
                    theme={theme}
                    isExample={title == "Examples"}
                    onClick={() => handleCardClick(title, text)}
                    key={index}
                  >
                    {text}
                  </StyledPaper>
                ))}
              </Box>
            </Grid>
          ))} */}

          {selectedAIApplicationObj && selectedAIApplicationObj.welcome_column1 && (
            <Grid item md={12} lg={4}>
              <Box sx={CARD_STYLE}>
                {/* {icon} */}
                <Typography variant="h6" component="p" mt={1}>
                  {selectedAIApplicationObj.welcome_column1.header}
                </Typography>
                {selectedAIApplicationObj.welcome_column1.messages.map(
                  (text, index) => (
                    <StyledPaper
                      className="sample_question"
                      theme={theme}
                      isExample={
                        selectedAIApplicationObj.welcome_column1.header ==
                        "Sample questions..."
                      }
                      onClick={() =>
                        handleCardClick(
                          selectedAIApplicationObj.welcome_column1.header,
                          text
                        )
                      }
                      key={index}
                    >
                      {text}
                    </StyledPaper>
                  )
                )}
              </Box>
            </Grid>
          )}

          {selectedAIApplicationObj && selectedAIApplicationObj.welcome_column2 && (
            <Grid item md={12} lg={4}>
              <Box sx={CARD_STYLE}>
                {/* {icon} */}
                <Typography variant="h6" component="p" mt={1}>
                  {selectedAIApplicationObj.welcome_column2.header}
                </Typography>
                {selectedAIApplicationObj.welcome_column2.messages.map(
                  (text, index) => (
                    <StyledPaper
                      id="sampleQuestion"
                      className="sample_question"
                      theme={theme}
                      isExample={
                        selectedAIApplicationObj.welcome_column2.header ==
                        "Sample questions..."
                      }
                      onClick={() =>
                        handleCardClick(
                          selectedAIApplicationObj.welcome_column2.header,
                          text
                        )
                      }
                      key={index}
                    >
                      {text}
                    </StyledPaper>
                  )
                )}
              </Box>
            </Grid>
          )}
        </Grid>
      </Grid>
    </Container>
  );
};

export default Hero;
