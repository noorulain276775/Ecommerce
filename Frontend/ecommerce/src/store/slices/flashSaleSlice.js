// store/slices/flashSaleSlice.js
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import API_URL from "../../constant";

// When this action is dispatched, it will call the api
export const fetchFlashSaleProducts = createAsyncThunk("productFlashSaleList", async () => {
  try {
    const response = await fetch(`${API_URL}/api/products/?flash_sale=true`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error fetching flash sale products:", error);
    throw error;
  }
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
      console.log("Error", action.error);
      state.isLoading = false;
      state.isError = true;
      state.data = null;
    });
  },
});

export default flashSaleSlice.reducer;
