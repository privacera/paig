import SendIcon from "@mui/icons-material/Send";
import LoadingButton from "@mui/lab/LoadingButton";
import { Box, Paper } from "@mui/material";
import React, { useContext, useState } from "react";
import DataContext from "../context/DataContext";
import Slider from "@mui/material/Slider";
import { styled } from "@mui/system";
import { blue, grey } from "@mui/material/colors";
import { StyledTextarea } from "../components/StyledComponents";

function DiscreteSliderMarks(props: {
  setSliderValue: (value: number) => void;
}) {
  return (
    <Box sx={{ width: 300, mt: 2 }}>
      <Slider
        aria-label="Temperature"
        defaultValue={0}
        valueLabelDisplay="auto"
        step={0.1}
        marks
        min={0}
        max={2}
        onChangeCommitted={(_e, value) => props.setSliderValue(value as number)}
      />
    </Box>
  );
}

const InputChat = ({
  chatLoading,
  handleInput
}: {
  chatLoading: boolean;
  handleInput: (message: string, temperature: number) => void;
}) => {
  const handlelogout = useContext(DataContext)?.handlelogout;
  const isCurrentUserConversation =
    useContext(DataContext)?.isCurrentUserConversation;
  const input = useContext(DataContext)?.input || "";
  const setInput = useContext(DataContext)?.setInput;
  const setChatLoader = useContext(DataContext)?.setChatLoader;

  const [sliderValue, setSliderValue] = useState(0);

  const handleInputAndClear = (message: string) => {
    setInput && setInput("");
    handleInput(message, sliderValue);
    setChatLoader && setChatLoader(true);
  };

  return (
    <Box
      sx={{
        width: "100%",
        display: "flex"
      }}
    >
      <Paper
        className="chat-input-box"
        sx={{
          p: 3,
          borderRadius: 2,
          display: "flex",
          flexGrow: 1,
          alignItems: "center",
          flexDirection: "column",
          width: "100%"
        }}
      >
        <Box
          sx={{
            display: "flex",
            flexGrow: 1,
            width: "100%"
          }}
        >
          <StyledTextarea
            id="textInput"
            maxRows={6}
            disabled={chatLoading || !isCurrentUserConversation}
            autoFocus={true}
            onKeyDown={(e) =>
              e.key === "Enter" &&
              !e.shiftKey &&
              input.trim() !== "" &&
              handleInputAndClear(input)
            }
            onChange={(e) => {
              setInput && setInput(e.target.value);
            }}
            value={input}
            placeholder="Ask a question"
          />

          <LoadingButton
            id="sendMsgBtn"
            onClick={() => handleInputAndClear(input)}
            startIcon={<SendIcon />}
            loading={chatLoading}
            loadingPosition="center"
            disabled={input == ""}
            sx={{
              "&.Mui-disabled": {
                cursor: "not-allowed"
              },
              "& .MuiCircularProgress-root": {
                color: blue[500]
              }
            }}
          ></LoadingButton>
        </Box>
        <Box>
          {/* <DiscreteSliderMarks setSliderValue={setSliderValue} /> */}
        </Box>
        {/*<Grid container justifyContent="space-between">
          <Grid item>
            <Typography
              sx={{
                textAlign: "center",
                marginTop: "20px"
              }}
              variant="subtitle2"
            >
              PAIG SecureChat LLM Model.
            </Typography>
          </Grid>
          <Grid item>
            <Button
              onClick={() => handlelogout && handlelogout()}
              color="error"
              sx={{
                marginTop: "12px"
              }}
            >
              Logout
            </Button>
          </Grid>
        </Grid>*/}
      </Paper>
    </Box>
  );
};

export default InputChat;
