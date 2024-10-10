import DarkModeOutlinedIcon from "@mui/icons-material/DarkModeOutlined";
import LightModeOutlinedIcon from "@mui/icons-material/LightModeOutlined";
import AccountCircleIcon from "@mui/icons-material/AccountCircle";
import { Box, Typography, useTheme } from "@mui/material";
import Button from "@mui/material/Button";
import React, { useContext, useState } from "react";
import { ColorModeContext } from "./App";
import { DRAWERWIDTH, NAVBARHEIGHT } from "./constants";
import DataContext from "./context/DataContext";
import { ReactComponent as Logo } from "./paig-ai_lockup-dark.svg";

import { IconButton, Menu, MenuItem, Divider } from "@mui/material";
import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown";

const ProfileDropdown = () => {
  const [userMenuOpen, setUserMenuOpen] = useState<HTMLElement | null>(null);

  const handleUserMenu = (event: React.MouseEvent<HTMLDivElement>) => {
    setUserMenuOpen(event.currentTarget);
  };

  const handleClose = () => {
    setUserMenuOpen(null);
  };

  const user = useContext(DataContext)?.userData;

  return (
    <div>
      <div
        className="account-dropdown"
        onClick={handleUserMenu}
        aria-describedby={Boolean(userMenuOpen) ? "menu-popover" : undefined}
      >
        <IconButton
          aria-label="account of current user"
          aria-controls="menu-appbar"
          aria-haspopup="true"
          color="inherit"
        >
          <AccountCircleIcon />
          <Typography ml={1} component="div">
            <Box className="font-bold" display="inline">
              {user?.user_name}
            </Box>
          </Typography>
          <ArrowDropDownIcon />
        </IconButton>
      </div>
      <Menu
        id={Boolean(userMenuOpen) ? "menu-popover" : ""}
        open={Boolean(userMenuOpen)}
        anchorEl={userMenuOpen}
        keepMounted
        classes={{ paper: "profile-menu-items" }}
        autoFocus={false}
        onClose={handleClose}
        anchorOrigin={{
          vertical: "bottom",
          horizontal: "center"
        }}
        transformOrigin={{
          vertical: "top",
          horizontal: "center"
        }}
      >
        <MenuItem onClick={useContext(DataContext)?.handlelogout}>
          Logout
        </MenuItem>
      </Menu>
    </div>
  );
};

const Header = () => {
  const theme = useTheme();
  const colorMode = useContext(ColorModeContext);
  const user = useContext(DataContext)?.userData;

  return (
    <Box
      sx={{
        zIndex: 100,
        position: "fixed",
        display: "flex",
        width: "100%",
        alignItems: "center",
        justifyContent: "center",
        p: 2,
        height: NAVBARHEIGHT,
        backgroundColor: "#001A6E"
      }}
    >
      <Box
        sx={{
          display: "flex",
          alignItems: "start",
          flex: 1,
          justifyContent: "start"
        }}
      >
        <Logo width="121px" height="28px" style={{ display: "block" }} />
      </Box>
      <Box
        sx={{
          ml: -2,
          pl: 2,
          color: "white",
          display: "flex",
          alignItems: "center"
        }}
      >
        {user && <ProfileDropdown />}
      </Box>
      {/* Commenting Theme switcher functionality for now and can be reused after uncommenting */}
      {/* <Box sx={{ width: DRAWERWIDTH, m: -2, pr: 2, display: 'flex' }}>
        <Button
          onClick={colorMode.toggleColorMode}
          aria-label='change the color mode'
          sx={{
            ml: 'auto',
          }}
          startIcon={theme.palette.mode === 'light' ? <DarkModeOutlinedIcon fontSize='large' /> : <LightModeOutlinedIcon fontSize='large' />}
          variant='outlined'
          color='inherit'
        >
          Use {theme.palette.mode === 'light' ? 'Dark' : 'Light'} Mode
        </Button>
      </Box> */}
    </Box>
  );
};

export default Header;
