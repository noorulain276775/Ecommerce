import React, { useEffect } from "react";
import { useSelector, useDispatch } from "react-redux";
import { fetchSeller } from "../../store/slices/sellerSlice";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Paper from "@mui/material/Paper";
import API_URL from "../../constant";

export default function Seller() {
  const dispatch = useDispatch();
  const sellerData = useSelector((state) => state.seller.data);
  console.log(sellerData)

  useEffect(() => {
    dispatch(fetchSeller());
  }, [dispatch]);

  return (
    <TableContainer component={Paper}>
      <Table sx={{ minWidth: 650 }} size="small" aria-label="a dense table">
        <TableHead>
          <TableRow>
            <TableCell align="left">Store Name</TableCell>
            <TableCell align="left">Description</TableCell>
            <TableCell align="left">Image</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {sellerData ? (
            sellerData.map((seller) => (
              <TableRow
                key={seller.id}
                sx={{ "&:last-child td, &:last-child th": { border: 0 } }}
              >
                <TableCell align="left">
                  {seller.name}
                </TableCell>
                <TableCell align="left">{seller.description}</TableCell>
                <TableCell align="left">
                  <img
                    src={`${API_URL}${seller.shop_logo}`}
                    alt="store-image"
                    style={{ maxWidth: "100px", maxHeight: "100px" }}
                  />
                </TableCell>
              </TableRow>
            ))
          ) : (
            <TableRow>
              <TableCell colSpan={3} align="center">
                Loading seller data...
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
