import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import API_URL from "../../constant";

export const doLogin = createAsyncThunk(
  "login/doLogin",
  async ({ phone, password }) => {
    try {
      const response = await fetch(`${API_URL}/login/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ phone, password }),
      });

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      return response.json();
    } catch (error) {
      console.error("Fetch error:", error);
      throw error;
    }
  }
);

const loginSlice = createSlice({
  name: "login",
  initialState: {
    phone: "",
    password: "",
    status: "idle",
    error: null,
    user: null,
  },

  extraReducers: (builder) => {
    builder
      .addCase(doLogin.pending, (state) => {
        state.status = "loading";
      })
      .addCase(doLogin.fulfilled, (state, action) => {
        state.status = "Succeeded";
        state.user = action.payload;
      })
      .addCase(doLogin.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.error.message;
      });
  },
});

export default loginSlice.reducer;
