import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import API_URL from "../../constant";

export const fetchBestSellers = createAsyncThunk("bestSellersList", async () => {
  try {
    const response = await fetch(`${API_URL}/api/products/?best_seller_product=true`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error fetching best sellers:", error);
    throw error;
  }
});

const bestSellersSlice = createSlice({
  name: "bestSellers",
  initialState: {
    isLoading: false,
    data: null,
    isError: false,
  },
  extraReducers: (builder) => {
    builder.addCase(fetchBestSellers.pending, (state, action) => {
      state.isLoading = true;
    });
    builder.addCase(fetchBestSellers.fulfilled, (state, action) => {
      state.isLoading = false;
      state.data = action.payload;
    });
    builder.addCase(fetchBestSellers.rejected, (state, action) => {
      console.log("Error", action.error);
      state.isLoading = false;
      state.isError = true;
      state.data = null;
    });
  },
});

export default bestSellersSlice.reducer;
