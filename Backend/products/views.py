from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Seller
from .serializers import SellerSerializer


class SellerView(APIView):
    def get(self, request):
        try:
            sellers = Seller.objects.all()
            serializer = SellerSerializer(sellers, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = SellerSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SellerDetailView(APIView):
    def put(self, request, id):
        try:
            try:
                seller = Seller.objects.get(id=id)
            except Seller.DoesNotExist:
                return Response({'error': 'Seller not found'}, status=status.HTTP_404_NOT_FOUND)

            serializer = SellerSerializer(
                seller, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def get(self, request, id):
        try:
            seller = Seller.objects.get(id=id)
            serializer = SellerSerializer(seller)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Seller.DoesNotExist:
            return Response({'error': 'Seller not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def delete(self, request, id):
        try:
            seller = Seller.objects.get(id=id)
            seller.delete()
            return Response({'message': 'Seller deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Seller.DoesNotExist:
            return Response({'error': 'Seller not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
