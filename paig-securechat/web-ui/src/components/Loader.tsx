import { Box, Divider, Grid, Skeleton, Stack } from "@mui/material";
import * as React from "react";

type DotLoaderProps = {
  withpadding?: boolean;
};

const DotLoader: React.FunctionComponent<DotLoaderProps> = (props) => {
  let loader = (
    <div className="loading-dots">
      <span className="loading-dots--dot"></span>
      <span className="loading-dots--dot"></span>
      <span className="loading-dots--dot"></span>
    </div>
  );

  if (props.withpadding) {
    loader = <div style={{ paddingTop: 100 }}>{loader}</div>;
  }
  return loader;
};

DotLoader.defaultProps = {
  withpadding: true
};

const getLoader = (type?: string) => {
  switch (type) {
    case "CHAT_LOADER":
      return (
        <Box sx={{ mx: "auto", maxWidth: "900px", mt: 1 }}>
          <Grid container direction="column" gap="10px">
            <Grid item xs={12}>
              <Box sx={{ ml: -8, maxWidth: "30%" }}>
                <Skeleton
                  sx={{ borderRadius: "8px" }}
                  variant="rectangular"
                  animation="wave"
                  height={35}
                />
              </Box>
            </Grid>
            <Grid item xs={12}>
              <Box sx={{ float: "right", width: "100%", maxWidth: "60%" }}>
                <Skeleton
                  sx={{ borderRadius: "8px" }}
                  variant="rectangular"
                  animation="wave"
                  height={55}
                />
              </Box>
            </Grid>
            <Grid item xs={12}>
              <Box sx={{ maxWidth: "60%" }}>
                <Skeleton
                  sx={{ borderRadius: "8px" }}
                  variant="rectangular"
                  animation="wave"
                  height={75}
                />
              </Box>
            </Grid>
            <Grid item xs={12}>
              <Box sx={{ float: "right", width: "100%", maxWidth: "50%" }}>
                <Skeleton
                  sx={{ borderRadius: "8px" }}
                  variant="rectangular"
                  animation="wave"
                  height={55}
                />
              </Box>
            </Grid>
            <Grid item xs={12}>
              <Box sx={{ maxWidth: "70%" }}>
                <Skeleton
                  sx={{ borderRadius: "8px" }}
                  variant="rectangular"
                  animation="wave"
                  height={85}
                />
              </Box>
            </Grid>
          </Grid>
        </Box>
      );
    case "CHAT_LOADER2":
      return (
        <Box display="grid" gap={1} sx={{ mx: "auto", maxWidth: "900px" }}>
          <Skeleton
            sx={{ borderRadius: "8px", float: "right" }}
            animation="wave"
            height={110}
          />
          <Skeleton
            sx={{ borderRadius: "8px" }}
            animation="wave"
            height={110}
          />
          <Box
            sx={{
              fright: 0,
              width: "100%",
              maxWidth: "50%"
            }}
          >
            <Skeleton
              sx={{ borderRadius: "8px" }}
              animation="wave"
              variant="rectangular"
              height={60}
            />
          </Box>
          <Skeleton
            sx={{ borderRadius: "8px", float: "right", right: 0 }}
            animation="wave"
            variant="rounded"
            width="70%"
            height={60}
          />
        </Box>
      );
    default:
      return (
        <Grid item>
          <Skeleton variant="text" animation="wave" />
          <Skeleton variant="text" animation="wave" />
          <Skeleton variant="text" animation="wave" />
          <Skeleton variant="text" animation="wave" />
          <Skeleton variant="text" animation="wave" />
        </Grid>
      );
  }
};

export { DotLoader, getLoader };
