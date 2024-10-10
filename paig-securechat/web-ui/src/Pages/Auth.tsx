import { Box, Button, Typography } from '@mui/material';
import React, { useContext, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import DataContext from '../context/DataContext';

export default function Auth() {
  const user = useContext(DataContext)?.userData;
  const navigate = useNavigate();

  useEffect(() => {
    if (user) navigate('/chat');
    else navigate('/login');
  }, [user]);

  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        height: '80vh',
      }}
    >
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          flexDirection: 'column',
        }}
      >
        <Typography variant='subtitle1' sx={{ mt: 2 }}>
          Welcome to PAIG SecureChat
        </Typography>
        <Typography variant='body1' sx={{ mb: 2 }}>
          Login to continue
        </Typography>
        <Box className='same_line' sx={{ display: 'flex', flexDirection: 'row', mt: 3 }}>
          <Button component={Link} to='/login' variant='contained' sx={{ mr: 2 }}>
            Login
          </Button>
        </Box>
      </Box>
    </Box>
  );
}
