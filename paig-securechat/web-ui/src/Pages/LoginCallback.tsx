// LoginCallback.tsx
import React, { useContext, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { postLoginApi } from "../Api/apis";
import { encryptData } from "../utils";
import DataContext from "../context/DataContext";
import { useSnackbar } from "notistack";
import { OktaAuth } from '@okta/okta-auth-js';
import {
  CircularProgress,
  Grid
} from "@mui/material";
import { Padding } from '@mui/icons-material';


const LoginCallback: React.FC = () => {
  const navigate = useNavigate();
  const handleAuth = useContext(DataContext)?.handleAuth;
  const { enqueueSnackbar } = useSnackbar();
  const storageData: any = localStorage.getItem('OktaAuthClient');
  const oktaData: any = JSON.parse(storageData);
  const OktaAuthClient =  new OktaAuth({
    issuer: oktaData.issuer,
    clientId: oktaData.client_id,
    redirectUri: window.location.origin + '/login/callback',
  });
  useEffect(() => {
    const handleAuthentication = async () => {
      try {
        let email: any = '';
        let accessToken: any, userInfo: any;
        if (OktaAuthClient.isLoginRedirect()) {
          const tokenData = await OktaAuthClient.token.parseFromUrl();
          let accessTokeData: any = tokenData.tokens.accessToken;
          accessToken = accessTokeData.accessToken;
          let idTokenData: any = tokenData.tokens.idToken;
          let userInfo: any = idTokenData.claims;
          email = userInfo.email;
        } else {
          const tokens = await OktaAuthClient.handleLoginRedirect();
          accessToken = OktaAuthClient.getAccessToken();
          userInfo = await OktaAuthClient.token.getUserInfo();
          email = userInfo.email;
        }
        if (accessToken === '') throw new Error('Invalid Access token');
        const res = await postLoginApi({ "user_name": email }, accessToken);
        localStorage.setItem("auth", encryptData(JSON.stringify(res.data)));
        if (handleAuth) {
            handleAuth(res.data);
            enqueueSnackbar("Login success", { variant: "success" });
            navigate("/chat");
        }
      } catch (error) {
        enqueueSnackbar("Invalid Credentials", { variant: "error" });
        navigate("/login");
        console.error('Error handling callback:', error);
      }
    };

    handleAuthentication();
  }, [history]);

  return <Grid
  container
  direction="row"
  justifyContent="center"
  alignItems="center"
  minHeight="80vh"
>
  <CircularProgress />
  <div style={{padding: '15px'}}> <span>Logging in...</span> </div>
</Grid>
};

export default LoginCallback;
