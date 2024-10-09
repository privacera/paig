import {
  CssBaseline,
  ThemeProvider,
  Toolbar,
  createTheme
} from "@mui/material";
import { SnackbarProvider } from "notistack";
import React from "react";
import { Route, Routes } from "react-router-dom";
import Hero from "./PageLayout/Hero";
import PageLayout from "./PageLayout/PageLayout";
import Auth from "./Pages/Auth";
import Chat, { FirstPrompt } from "./Pages/Chat";
import Login from "./Pages/Login";
import LoginCallback from './Pages/LoginCallback';
import Header from "./Header";
import { DataProvider } from "./context/DataContext";
import { lightTheme, darkTheme } from "./theme";
import "./App.scss";
import { DotLoader } from "./components/Loader";

export const ColorModeContext = React.createContext({
  toggleColorMode: () => {}
});

const App = (): React.ReactElement => {
  // Commenting Theme switcher functionality for now and can be reused after uncommenting
  // const [mode, setMode] = React.useState<"light" | "dark">(() => {
  //   const savedMode = localStorage.getItem("mode");
  //   return savedMode ? (savedMode as "light" | "dark") : "dark";
  // });

  const [mode, setMode] = React.useState<string>("light");

  React.useEffect(() => {
    localStorage.setItem("mode", mode);
  }, [mode]);

  const colorMode = React.useMemo(
    () => ({
      toggleColorMode: () => {
        setMode((prevMode) => (prevMode === "light" ? "dark" : "light"));
      }
    }),
    [setMode]
  );

  const updatedTheme = React.useMemo(
    () => createTheme(mode === "light" ? lightTheme : darkTheme),
    [mode]
  );
  return (
    <ColorModeContext.Provider value={colorMode}>
      <ThemeProvider theme={updatedTheme}>
        <CssBaseline>
          <DataProvider>
            <SnackbarProvider
              maxSnack={3}
              autoHideDuration={3000}
              anchorOrigin={{
                vertical: "top",
                horizontal: "right"
              }}
            >
              <Routes>
                <Route path="/login" element={<Login />} />
                <Route path="/" element={<Auth />} />
                <Route path="/login/callback" element={
                  <>
                  <Header />
                  <Toolbar />
                  <LoginCallback/>
                  </>
                } />
                <Route
                  path="/chat/*"
                  element={
                    <>
                    <Header />
                    <Toolbar />
                    <PageLayout>
                      <Routes>
                        <Route path="" element={<Hero />} />
                        <Route path="c/:id" element={<Chat />} />
                        <Route path="new" element={<FirstPrompt />} />
                      </Routes>
                    </PageLayout>
                    </>
                  }
                />
              </Routes>
            </SnackbarProvider>
          </DataProvider>
        </CssBaseline>
      </ThemeProvider>
    </ColorModeContext.Provider>
  );
};

export default App;
