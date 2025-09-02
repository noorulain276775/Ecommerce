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

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || "Login failed");
      }

      // Store token in localStorage
      if (data.token) {
        localStorage.setItem('authToken', data.token);
        localStorage.setItem('user', JSON.stringify(data.user));
      }

      return data;
    } catch (error) {
      console.error("Login error:", error);
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
    user: JSON.parse(localStorage.getItem('user')) || null,
    token: localStorage.getItem('authToken') || null,
  },

  extraReducers: (builder) => {
    builder
      .addCase(doLogin.pending, (state) => {
        state.status = "loading";
      })
      .addCase(doLogin.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.user = action.payload.user;
        state.token = action.payload.token;
        state.error = null;
      })
      .addCase(doLogin.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.error.message;
        state.user = null;
        state.token = null;
      });
  },
});

export default loginSlice.reducer;
