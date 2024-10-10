import { styled } from "@mui/system";
import { blue, grey } from "@mui/material/colors";
import { Theme } from "@mui/material/styles";
import { Paper, TextareaAutosize } from "@mui/material";

const StyledPaper = styled(Paper)<{ theme: Theme; isExample: boolean }>(
  ({ theme, isExample }) => `
  margin-top:16px;
  font-size:14px;
  padding:16px;
  color: ${theme.palette.mode === "dark" ? grey[300] : grey[900]};
  background: ${theme.palette.mode === "dark" ? "#0A1929" : "#fff"};
  background-image: linear-gradient(rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.05));
  ${
    isExample &&
    `
    &:hover {
      border-color: ${blue[400]};
      background: ${theme.palette.mode === "dark" ? "#0a1929" : "#F4F4F4"};
      cursor: pointer;
    }
    `
  }
  `
);

const StyledTextarea = styled(TextareaAutosize)(
  ({ theme }) => `
      resize:none;
      width:100%;
      font-weight: 400;
      line-height: 1.5;
      padding: 12px;
      border-radius: 8px;
      resize: none !important; 
      color: ${theme.palette.mode === "dark" ? grey[300] : grey[900]};
      background: ${theme.palette.mode === "dark" ? "#0a1929" : "#fff"};

      &:hover {
        border-color: ${blue[400]};
      }

      &:focus {
        border-color: ${theme.palette.mode === "dark" ? grey[300] : grey[900]};
      }

      &:disabled {
        cursor: not-allowed ;
      }
      `
);

export { StyledPaper, StyledTextarea };
