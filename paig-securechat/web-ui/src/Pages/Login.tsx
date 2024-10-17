import {
  Button,
  Box,
  Paper,
  TextField,
  Typography
} from "@mui/material";
import axios from "axios";
import { useSnackbar } from "notistack";
import React, { useContext, useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import DataContext from "../context/DataContext";
import User from "../models/userModel";
import { encryptData } from "../utils";
import { postLoginApi, getServerConfig } from "../Api/apis";
import Alert from '@mui/material/Alert';
import { OktaAuth } from '@okta/okta-auth-js';
import { LogoIcon } from "../icons";
import {
  CircularProgress,
  Backdrop
} from "@mui/material";

const Login = () => {
  const [showSSOError, setshowSSOError] = React.useState(false);
  const [showLoader, setshowLoader] = React.useState(false);
  const sessionCleanUp = useContext(DataContext)?.sessionCleanUp;
  const setServerConfig = useContext(DataContext)?.setServerConfig;
  const ServerConfig = useContext(DataContext)?.ServerConfig;
  const setOktaAuthClient = useContext(DataContext)?.setOktaAuthClient;
  const OktaAuthClient = useContext(DataContext)?.OktaAuthClient;
  const [userName, setUserName] = useState<string>("");
  const [Password, setPassword] = useState<string>("");
  useEffect(() => {
    sessionCleanUp && sessionCleanUp();
    getAllServerConfig();
    if (ServerConfig && ServerConfig.single_user_mode) setUserName && setUserName(ServerConfig.default_user)
  }, []);



  const getAllServerConfig = async () => {
    if (!ServerConfig) {
      try {
        const res = await getServerConfig();
        setServerConfig && setServerConfig(res.data);
        await createOktaAuthClient(res.data);
        if (res.data.single_user_mode) {
          setUserName && setUserName(res.data.default_user);
        }
      } catch (err: any) {
        enqueueSnackbar(err.message, {
          variant: "error"
        });
      }
    }
  };


  const createOktaAuthClient = async (data: any) => {
    if (data && data.okta.enabled && data.single_user_mode === false) {
      var oktaAuth: any;
      try {
        oktaAuth = new OktaAuth({
          issuer: data.okta.issuer,
          clientId: data.okta.client_id,
          redirectUri: window.location.origin + '/login/callback',
        }); 
      } catch (error) {
        console.error('Error initializing Okta:', error);
        oktaAuth = null;
      }
      setOktaAuthClient && setOktaAuthClient(oktaAuth);
      // Storing data in localStorage
      localStorage.setItem('OktaAuthClient', JSON.stringify(data.okta));
      // check query params for automatic redirection
      const iss = new URLSearchParams(window.location.search).get('iss');
      if (oktaAuth && iss && iss === data.okta.issuer) handleOktaLogin(oktaAuth)
    }
  }
  const history = useNavigate();
  // const [email, setEmail] = useState<string>("");
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();
  const handleAuth = useContext(DataContext)?.handleAuth;

  const handleLogin = async () => {
    setshowSSOError(false);
    if (!userName)
      return enqueueSnackbar("Please fill all username", { variant: "error" });
    try {
      setshowLoader(true);
      const res = await postLoginApi({ "user_name": userName });
      localStorage.setItem("auth", encryptData(JSON.stringify(res.data)));
      if (handleAuth) {
        handleAuth(res.data);
        enqueueSnackbar("Login success", { variant: "success" });
        navigate("/chat");
        setshowLoader(false);
      }
    } catch (err) {
      setshowLoader(false);
      enqueueSnackbar("Invalid Credentials", { variant: "error" });
    }
  };

  const handlebBasicAuthLogin = async () => {
    setshowSSOError(false);
    if (!userName)
      return enqueueSnackbar("Please fill all username", { variant: "error" });
    if (!Password)
      return enqueueSnackbar("Please fill password", { variant: "error" });
    try {
      setshowLoader(true);
      const res = await postLoginApi({ "user_name": userName, "password": Password });
      localStorage.setItem("auth", encryptData(JSON.stringify(res.data)));
      if (handleAuth) {
        handleAuth(res.data);
        enqueueSnackbar("Login success", { variant: "success" });
        navigate("/chat");
        setshowLoader(false);
      }
    } catch (err) {
      setshowLoader(false);
      enqueueSnackbar("Invalid Credentials", { variant: "error" });
    }
  };

  const handleOktaLogin = async (oktaAuthObj: any = null) => {
    try {
      setshowLoader(true);
      if (oktaAuthObj) await oktaAuthObj.signInWithRedirect();
      else await OktaAuthClient.signInWithRedirect();
      setshowLoader(false);
    } catch (error) {
      setshowSSOError(true);
      setshowLoader(false);
      console.error('Error logging in:', error);
    }
  };

  const is_okta_enabled = ServerConfig && ServerConfig.okta && ServerConfig.okta.enabled && ServerConfig.single_user_mode === false;
  const is_basic_auth_enabled = ServerConfig && ServerConfig.basic_auth && ServerConfig.basic_auth.enabled && ServerConfig.single_user_mode === false;
  const is_signle_user_mode = ServerConfig && ServerConfig.single_user_mode;

  return (
    <Box
    display="flex"
    justifyContent="center"
    alignItems="center"
    minHeight="100vh"
    >
      <Backdrop
          sx={{ color: '#fff', zIndex: (theme: any) => theme.zIndex.drawer + 1 }}
          open={showLoader}
        >
        <CircularProgress color="inherit" />
      </Backdrop>
      <Paper className={"login-container " + ((is_okta_enabled && !is_basic_auth_enabled) ? "sso-login-enable" : "")} sx={{ padding: 5}}>
        <div className="login-logo">
          <LogoIcon  sx={{ width: '6em', height: '2.5em'}}/>
        </div>
        <div className="login-element">
            <Typography variant="h5">
              SecureChat Login
            </Typography>
        </div>
          { (is_basic_auth_enabled || !is_okta_enabled) ?
            <div className="login-element">
              <Alert severity="info"> Your name is used to store history</Alert>
            </div>
          : null }
            { showSSOError ?
            <Alert severity="warning">Unable to sign in to your account using single sign-on. Please contact your administrator for assistance.</Alert>
           : null }
           { (is_basic_auth_enabled || !is_okta_enabled) ?
          <div className="login-element">
                <TextField
                  id="userNameField"
                  fullWidth={true}
                  variant="outlined"
                  label="Username"
                  value={userName}
                  onKeyDown={(e) =>
                    e.code === "Enter" && userName !== "" && (is_basic_auth_enabled ? handlebBasicAuthLogin() : handleLogin())
                  }
                  onChange={(e) => setUserName(e.target.value)}
                  disabled={ServerConfig && ServerConfig.single_user_mode}
                />
          </div>
            : null }

          { (is_basic_auth_enabled && !is_signle_user_mode) ?
          <div className="login-element">
                <TextField
                  id="password"
                  fullWidth={true}
                  variant="outlined"
                  label="Password"
                  value={Password}
                  type="password"
                  onKeyDown={(e) =>
                    e.code === "Enter" && Password !== "" && handlebBasicAuthLogin()
                  }
                  onChange={(e) => setPassword(e.target.value)}
                />
          </div>
            : null}
          <div className="login-element">
            { (is_basic_auth_enabled || !is_okta_enabled) ?

            <Button
              className="login-button"
              id="loginButton"
              variant="contained"
              onClick={is_basic_auth_enabled ? handlebBasicAuthLogin : handleLogin}
              fullWidth={true}
              disabled={!ServerConfig}
            >
              Login
            </Button>
             : null}
            { (is_basic_auth_enabled || !is_okta_enabled) ?
            <p className="or-for-sso">
              <span className="or-dash"></span>
              <strong><span className="or-text">OR</span></strong>
              <span className="or-dash"></span>
            </p>
            : null}
            <Button
              className="login-button"
              id="loginOktaButton"
              variant="contained"
              onClick={() => handleOktaLogin()}
              fullWidth={true}
              disabled={!ServerConfig || (!is_okta_enabled)}
            >
              Login With SSO
            </Button>
          </div>
      </Paper>
    </Box>
  );
};

export default Login;
