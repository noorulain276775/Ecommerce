// store/slices/sellerSlice.js
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import API_URL from "../../constant";

// When this action is dispatched, it will call the api
export const fetchFlashSaleProducts = createAsyncThunk("productFlashSaleList", async () => {
  const response = await fetch(`${API_URL}/api/products/?flash_sale=true`);
  return response.json();
});
const flashSaleSlice = createSlice({
  name: "flashSale",
  initialState: {
    isLoading: false,
    data: null,
    isError: false,
  },
  extraReducers: (builder) => {
    builder.addCase(fetchFlashSaleProducts.pending, (state, action) => {
      state.isLoading = true;
    });
    builder.addCase(fetchFlashSaleProducts.fulfilled, (state, action) => {
      state.isLoading = false;
      state.data = action.payload;
    });
    builder.addCase(fetchFlashSaleProducts.rejected, (state, action) => {
      console.log("Error", action.payload);
      state.isError = true;
    });
  },
});

export default flashSaleSlice.reducer;
