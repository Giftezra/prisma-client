from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from main.models import BookedAppointment,ServiceType, ValetType, AddOns

""" The view is used to define the structure of the booking api for the client.  """
class BookingView(APIView):
    permission_classes = [IsAuthenticated]
    """ Action handlers designed to route the url to the appropriate function """
    action_handlers = {
        'get_service_type' : 'get_service_type',
        'get_valet_type' : 'get_valet_type',
        'create_booking' : 'create_booking',
        'cancel_booking' : 'cancel_booking',
        'reschedule_booking' : 'reschedule_booking',
        'get_add_ons' : 'get_add_ons',
    }
    """ Here we will override the crud methods and define the methods that would route the url to the appropriate function """
    def get(self, request, *args, **kwargs):
        action = kwargs.get('action')
        if action not in self.action_handlers:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)
        handler = getattr(self, self.action_handlers[action])
        return handler(request)
    
    def post(self, request, *args, **kwargs):
        action = kwargs.get('action')
        if action not in self.action_handlers: 
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)
        handler = getattr(self, self.action_handlers[action])
        return handler(request)
    
    def patch(self, request, *args, **kwargs):
        action = kwargs.get('action')
        if action not in self.action_handlers:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)
        handler = getattr(self, self.action_handlers[action])
        return handler(request)
    
    """ These are the methods which will serve the user their request using the action handlers
        to get the methods and route then through the get, post, patch given the method passed in the 
        client api
    """

    def get_service_type(self, request):
        """ Get the service type predefined by the admin in the system.
            ARGS : void
            RESPONSE : ServiceTypeProps[]
            {
                id : string
                name : string
                description : string[]
                price : number
                duration : number
            }
        """
        try:
            service_type = ServiceType.objects.all()
            service_type_data = []
            # Here we could use the serializer to get the data in the proper format,
            # but i always prefer to destructure it manually
            for service in service_type:
                service_items = {
                    "id" : service.id,
                    "name" : service.name,
                    "description" : service.description,
                    "price" : service.price,
                    "duration" : service.duration
                }
                service_type_data.append(service_items)
            return Response(service_type_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
    def get_valet_type(self, request):
        """ Get the valet type predefined by the admin in the system.
            ARGS : void
            RESPONSE : ValetTypeProps[]
            {
                id : string
                name : string
                description : string
            }
        """
        try:
            valet_type = ValetType.objects.all()
            valet_type_data = []
            for valet in valet_type:
                valet_items = {
                    "id" : valet.id,
                    "name" : valet.name,
                    "description" : valet.description
                }
                valet_type_data.append(valet_items)
            return Response(valet_type_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

    def cancel_booking(self, request):
        """ Cancel a booking for the user.
            ARGS : void
            RESPONSE : void
            QUERY_PARAMS : booking_id : string
        """
        booking_id = request.query_params.get('booking_id')
        try:
            booking = BookedAppointment.objects.get(id=booking_id)
            booking.status = 'cancelled'
            booking.save()
            return Response({'message': f'You have cancelled your booking for {booking.vehicle.vehicle_name} on {booking.booking_date}'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def reschedule_booking(self, request):
        pass

    

    def create_booking(self, request):
        pass



    def get_add_ons(self, request):
        """ Get the add ons for the user to choose from
            ARGS : void
            RESPONSE : AddOnsProps[]
            {
                id : string
                name : string
                price : number
                description : string
                extra_duration : number 
            }
        """
        try:
            add_ons = AddOns.objects.all()
            add_ons_data = []
            for add_on in add_ons:
                add_on_items = {
                    "id" : add_on.id,
                    "name" : add_on.name,
                    "price" : add_on.price,
                    "description" : add_on.description,
                    "extra_duration" : add_on.extra_duration
                }
                add_ons_data.append(add_on_items)
            return Response(add_ons_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)