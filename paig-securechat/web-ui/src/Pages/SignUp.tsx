import { useState } from "react";
import {
  Box,
  Button,
  Container,
  Grid,
  Link,
  Paper,
  TextField,
  Typography
} from "@mui/material";
import { LogoIcon } from "../icons";
import { Link as RouterLink, useNavigate } from "react-router-dom";
import React from "react";
import { useSnackbar } from "notistack";
import { encryptData } from "../utils";
import { postSignupApi } from "../Api/apis";

export default function Signup() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();

  const handleSignup = async () => {
    if (!email || !password) {
      enqueueSnackbar("Please fill all fields", { variant: "error" });
      return;
    }
    try {
      const res = await postSignupApi({
        email: email,
        password,
        name: "privcaera_user"
      });
      localStorage.setItem("auth", encryptData(JSON.stringify(res.data)));
      navigate("/chat");
    } catch (err: any) {
      enqueueSnackbar(err.response.data.message, { variant: "error" });
    }
  };

  return (
    <Container maxWidth="sm">
      <Paper elevation={3} style={{ marginTop: "24vh", padding: "32px" }}>
        <Grid container direction="column" alignItems="center" spacing={2}>
          <Grid item>
            <Typography variant="h5" sx={{ mb: 2 }}>
              Create your account
            </Typography>
          </Grid>
          <Grid item>
            <TextField
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              variant="outlined"
              fullWidth
              margin="normal"
              label="UserName"
              sx={{
                width: "488px"
              }}
            />
          </Grid>
          {/* <Grid item>
            <TextField  value={name} onChange={(e) => setName(e.target.value)} variant='outlined' fullWidth margin='normal' label='Name' sx={{
              width: '488px',
            }} />
          </Grid> */}
          <Grid item>
            <TextField
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              variant="outlined"
              fullWidth
              margin="normal"
              label="Password"
              type="password"
              sx={{
                width: "488px"
              }}
            />
          </Grid>

          <Button
            onClick={() => handleSignup()}
            variant="contained"
            sx={{ mt: 2, mb: 1 }}
          >
            Signup
          </Button>
          <Grid item>
            <Typography variant="body1">
              Already have an account?{" "}
              <Link
                component={RouterLink}
                to="/login"
                color="primary"
                sx={{
                  textDecoration: "none"
                }}
              >
                Login
              </Link>
            </Typography>
          </Grid>
        </Grid>
      </Paper>
    </Container>
  );
}
