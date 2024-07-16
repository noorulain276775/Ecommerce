import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import API_URL from "../../constant";

export const doRegister = createAsyncThunk(
  "register/doRegister",
  async ({
    phone,
    password,
    first_name,
    last_name,
    dateOfBirth,
    password2,
  }) => {
    try {
      const requestBody = { first_name, last_name, phone, password, password2 };
      if (dateOfBirth) {
        let dateObj = new Date(dateOfBirth);
        let year = dateObj.getFullYear();
        let month = String(dateObj.getMonth() + 1).padStart(2, '0');
        let day = String(dateObj.getDate()).padStart(2, '0'); 
        let date_of_birth = `${year}-${month}-${day}`;
        requestBody.date_of_birth = date_of_birth;
        console.log(requestBody.date_of_birth);
      }
     


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
    first_name: "",
    last_name: "",
    phone: "",
    password: "",
    date_of_birth: "",
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
