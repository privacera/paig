import * as React from 'react';
import TextareaAutosize, { TextareaAutosizeProps } from '@mui/base/TextareaAutosize';
import { styled } from '@mui/system';
import { blue, grey } from '@mui/material/colors';

export default function EmptyTextArea({ maxRows, placeholder, disabled, autoFocus, onKeyDown, onChange, value }: TextareaAutosizeProps) {
  const StyledTextarea = styled(TextareaAutosize as any)(
    ({ theme }) => `
    font-size: 1rem;
    font-weight: 400;
    line-height: 1.5;
    padding: 12px;
    border-radius: 12px 12px 0 12px;
    resize: none !important; 
    color: ${theme.palette.mode === 'dark' ? grey[300] : grey[900]};
    background: ${theme.palette.mode === 'dark' ? grey[900] : '#fff'};
    border: 1px solid ${theme.palette.mode === 'dark' ? grey[700] : grey[200]};
    box-shadow: 0px 2px 2px ${theme.palette.mode === 'dark' ? grey[900] : grey[50]};
  
    &:hover {
      border-color: ${blue[400]};
    }
  
    &:focus {
      border-color: ${blue[400]};
      box-shadow: 0 0 0 3px ${theme.palette.mode === 'dark' ? blue[500] : blue[200]};
    }
  
    // firefox
    &:focus-visible {
      outline: 0;
    }
  `
  );

  return (
    <StyledTextarea
      maxRows={maxRows}
      aria-label='maximum height'
      placeholder={placeholder}
      disabled={disabled}
      autoFocus={autoFocus}
      onKeyDown={onKeyDown}
      onChange={onChange}
      value={value}
      sx={{
        width: '100%',
        '.Mui-disabled': {
          cursor: 'not-allowed',
        },
      }}
    />
  );
}
