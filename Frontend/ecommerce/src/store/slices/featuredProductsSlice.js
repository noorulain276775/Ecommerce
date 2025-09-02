import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import API_URL from "../../constant";

export const fetchFeaturedProducts = createAsyncThunk("featuredProductsList", async () => {
  try {
    const response = await fetch(`${API_URL}/api/products/?featured_product=true`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error fetching featured products:", error);
    throw error;
  }
});

const featuredProductsSlice = createSlice({
  name: "featuredProducts",
  initialState: {
    isLoading: false,
    data: null,
    isError: false,
  },
  extraReducers: (builder) => {
    builder.addCase(fetchFeaturedProducts.pending, (state, action) => {
      state.isLoading = true;
    });
    builder.addCase(fetchFeaturedProducts.fulfilled, (state, action) => {
      state.isLoading = false;
      state.data = action.payload;
    });
    builder.addCase(fetchFeaturedProducts.rejected, (state, action) => {
      console.log("Error", action.error);
      state.isLoading = false;
      state.isError = true;
      state.data = null;
    });
  },
});

export default featuredProductsSlice.reducer;
