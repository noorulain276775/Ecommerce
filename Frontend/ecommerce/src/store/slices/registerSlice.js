import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import API_URL from "../../constant";

export const doRegister = createAsyncThunk(
    "register/doRegister",
    async ({ first_name, last_name, phone, password, date_of_birth }) => {
      try {
        const requestBody = { first_name, last_name, phone, password };
        if (date_of_birth) requestBody.date_of_birth = date_of_birth;
  
        const response = await fetch(`${API_URL}/register/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(requestBody),
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

const registerSlice = createSlice({
  name: "register",
  initialState: {
    first_name:"",
    last_name:"",
    phone: "",
    password: "",
    date_of_birth:"",
    status: "idle",
    error: null,
    user: null,
  },

  extraReducers: (builder) => {
    builder
      .addCase(doRegister.pending, (state) => {
        state.status = "loading";
      })
      .addCase(doRegister.fulfilled, (state, action) => {
        state.status = "Succeeded";
        state.user = action.payload;
      })
      .addCase(doRegister.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.error.message;
      });
  },
});

export default registerSlice.reducer;
