// store/slices/sellerSlice.js
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import API_URL from "../../constant";

// When this action is dispatched, it will call the api
export const fetchSeller = createAsyncThunk("sellerList", async () => {
  const response = await fetch(`${API_URL}/api/seller`);
  return response.json();
});
const sellerSlice = createSlice({
  name: "seller",
  initialState: {
    isLoading: false,
    data: null,
    isError: false,
  },
  extraReducers: (builder) => {
    builder.addCase(fetchSeller.pending, (state, action) => {
      state.isLoading = true;
    });
    builder.addCase(fetchSeller.fulfilled, (state, action) => {
      state.isLoading = false;
      state.data = action.payload;
    });
    builder.addCase(fetchSeller.rejected, (state, action) => {
      console.log("Error", action.payload);
      state.isError = true;
    });
  },
});

export default sellerSlice.reducer;
