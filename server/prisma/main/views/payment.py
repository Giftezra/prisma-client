
# from rest_framework.response import Response
# from rest_framework import status
# from management.models import Company
# from management.models import SubscriptionTier
# from management.models import User
# import stripe
# from django.conf import settings
# from rest_framework.permissions import IsAuthenticated
# from management.models import SubscriptionPlan
# from staff.models import Staff
# from datetime import datetime, timedelta, timezone
# from management.models import Overage, Billing, SubscriptionHistory
# from rest_framework.views import APIView

# # Initialize Stripe with your secret key
# stripe.api_key = settings.STRIPE_SECRET_KEY


# class ManagementPaymentView(APIView):
#     """
#     Class-based view for managing payment and subscription operations.
    
#     Handles all payment-related actions including:
#     - Creating payment sheets for Stripe
#     - Managing subscription tiers and plans
#     - Processing subscription updates
#     - Handling Stripe webhooks
#     """
#     permission_classes = [IsAuthenticated]
    
#     def dispatch(self, request, *args, **kwargs):
#         """
#         Centralized authorization logic for owner users.
        
#         Ensures only owner users can access payment and subscription management features.
#         """
#         if not request.user.is_owner:
#             return Response(
#                 {'error': 'You are not authorized to access this resource'}, 
#                 status=status.HTTP_403_FORBIDDEN
#             )
#         return super().dispatch(request, *args, **kwargs)
    

#     def get(self, request, action=None):
#         """
#         Handle GET requests for different payment actions.
        
#         Args:
#             request: The HTTP request object
#             action: The specific action to perform (subscription_tiers, current_plan, etc.)
#         """
#         if action == 'subscription_tiers':
#             return self.get_subscription_tiers(request)
#         elif action == 'current_plan':
#             return self.get_current_plan(request)
#         elif action == 'subscription_history':
#             return self.get_subscription_history(request)
#         else:
#             return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

#     def post(self, request, action=None):
#         """
#         Handle POST requests for payment actions.
        
#         Args:
#             request: The HTTP request object
#             action: The specific action to perform (create_payment_sheet, update_subscription_plan, etc.)
#         """
#         if action == 'create_payment_sheet':
#             return self.create_payment_sheet(request)
#         elif action == 'update_subscription_plan':
#             return self.update_subscription_plan(request)
#         elif action == 'stripe_webhook':
#             return self.stripe_webhook(request)
#         else:
#             return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

#     def create_payment_sheet(self, request):
#         """
#         Create a payment sheet for Stripe payment processing.
        
#         Creates a Stripe payment intent and ephemeral key for client-side payment processing.
#         """
#         try:
#             # Get amount and metadata from request
#             amount = request.data.get('amount', 0)
#             metadata = request.data.get('metadata', {})
#             plan_id = metadata.get('plan_id', None)
#             billing_period = metadata.get('billing_period', None)

#             # Get the company object associated with the user
#             company = Company.objects.get(owner=request.user)
            
#             # Create Stripe customer
#             customer = stripe.Customer.create()
            
#             # Create payment intent with calculated amount
#             payment_intent = stripe.PaymentIntent.create(
#                 amount=amount,  # Amount in cents from the frontend
#                 currency='gbp',
#                 customer=customer.id,
#                 automatic_payment_methods={
#                     'enabled': True,
#                 },
#                 metadata={
#                     'company_id': company.id,
#                     'plan_id': plan_id,
#                     'billing_period': billing_period,
#                     'user_id': request.user.id,
#                 }
#             )
            
#             # Create ephemeral key for client-side access
#             ephemeral_key = stripe.EphemeralKey.create(
#                 customer=customer.id,
#                 stripe_version='2022-11-15',
#             )
            
#             return Response({
#                 'paymentIntent': payment_intent.client_secret,
#                 'ephemeralKey': ephemeral_key.secret,
#                 'customer': customer.id,
#             }, status=status.HTTP_200_OK)
            
#         except Exception as e:
#             return Response(
#                 {'error': str(e)}, 
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )


#     def get_subscription_tiers(self, request):
#         """
#         Get all subscription tiers from the database.
        
#         Returns cached data if available, otherwise queries the database.
#         """
#         try:
#             # Get all subscription tiers
#             subscription_tiers = SubscriptionTier.objects.all()
#             subscription_tiers_data = []
            
#             for tier in subscription_tiers:
#                 subscription_tiers_data.append({
#                     'id': tier.id,
#                     'name': tier.name,
#                     'description': tier.description,
#                     'features': tier.features,
#                     'numberOfEmployees': tier.numberOfEmployees,
#                     'rate': tier.rate,
#                     'isPopular': tier.is_popular,
#                     'overage_rate': tier.overage_rate,
#                     'is_custom': tier.is_custom,
#                     'minimum_employees': tier.minimum_employees,
#                 })
            
#             return Response({'subscriptionTiers': subscription_tiers_data}, status=status.HTTP_200_OK)
            
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#     def get_current_plan(self, request):
#         """
#         Get the current subscription plan for the authenticated user's company.
        
#         Includes employee count, plan limits, and overage calculations.
#         """
#         try:
#             # Get the company object associated with the user
#             company = Company.objects.get(owner=request.user)
            
#             # Get the active subscription plan
#             subscription_plan = SubscriptionPlan.objects.filter(
#                 company=company, 
#                 is_active=True
#             ).first()
            
#             # Count active employees
#             active_employees = Staff.objects.filter(
#                 company=company, 
#                 is_active=True
#             ).count()
            
#             # Calculate overage count
#             plan_limit = subscription_plan.tier.numberOfEmployees
#             overage_count = max(0, active_employees - plan_limit)

#             subscription_plan_data = {
#                 'plan_name': subscription_plan.tier.name,
#                 'billing_cycle': subscription_plan.billing_cycle,
#                 'current_employees': active_employees,
#                 'plan_limit': plan_limit,
#                 'overage_count': overage_count,
#                 'overage_fees': subscription_plan.tier.overage_rate,
#                 'start_date': subscription_plan.start_date,
#                 'renewal_date': subscription_plan.renewal_date,
#                 'status': subscription_plan.is_active,
#             }
            
#             return Response({'subscription_plan': subscription_plan_data}, status=status.HTTP_200_OK)
            
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

#     def update_subscription_plan(self, request):
#         """
#         Update the subscription plan for a company.
        
#         Deactivates existing plans and creates new subscription with history tracking.
#         """
#         try:
#             # Get required data from request
#             tier_id = request.data.get('tier_id')
#             billing_period = request.data.get('billing_period')

#             # Validate company and tier existence
#             try:
#                 company = Company.objects.get(owner=request.user)
#                 tier = SubscriptionTier.objects.get(id=tier_id)
#             except Company.DoesNotExist:
#                 return Response(
#                     {'error': 'Company not found'}, 
#                     status=status.HTTP_404_NOT_FOUND
#                 )
#             except SubscriptionTier.DoesNotExist:
#                 return Response(
#                     {'error': 'Subscription tier not found'}, 
#                     status=status.HTTP_404_NOT_FOUND
#                 )
            
#             # Calculate start and renewal dates
#             start_date = datetime.now(timezone.utc).date()
#             renewal_date = start_date + timedelta(
#                 days=365 if billing_period == 'annually' else 30
#             )
            
#             # Deactivate any existing active plan
#             SubscriptionPlan.objects.filter(
#                 company=company, 
#                 is_active=True
#             ).update(is_active=False)
            
#             # Create new subscription plan
#             new_plan = SubscriptionPlan.objects.create(
#                 company=company,
#                 tier=tier,
#                 billing_cycle=billing_period,
#                 start_date=start_date,
#                 renewal_date=renewal_date,
#                 is_active=True,
#             )
            
#             # Create subscription history record
#             SubscriptionHistory.objects.create(
#                 subscription=new_plan,
#                 start_date=start_date,
#                 renewal_date=renewal_date,
#                 is_active=True
#             )

#             return Response(
#                 {'message': 'Subscription updated successfully'}, 
#                 status=status.HTTP_200_OK
#             )

#         except Exception as e:
#             return Response(
#                 {'error': f'Error updating subscription plan: {str(e)}'}, 
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )


#     def get_subscription_history(self, request):
#         """
#         Get the subscription history for the authenticated user's company.
        
#         Returns ordered history with status determination.
#         """
#         try:
#             # Get the associated company
#             company = Company.objects.get(owner=request.user)
            
#             # Get subscription history ordered by start date (newest first)
#             subscription_history = SubscriptionHistory.objects.filter(
#                 subscription__company=company
#             ).select_related('subscription', 'subscription__tier').order_by('-start_date')
            
#             subscription_history_data = []
            
#             for history in subscription_history:
#                 # Skip if subscription or tier is None
#                 if not history.subscription or not history.subscription.tier:
#                     continue
                    
#                 # Determine status
#                 now = timezone.now().date()
#                 if history.subscription.is_active:
#                     history_status = 'active'
#                 elif history.renewal_date < now:
#                     history_status = 'expired'
#                 else:
#                     history_status = 'active'  # Safety fallback

#                 subscription_history_data.append({
#                     'id': history.id,
#                     'start_date': history.start_date,
#                     'renewal_date': history.renewal_date,
#                     'tier': history.subscription.tier.name,
#                     'tier_id': history.subscription.tier.id,
#                     'billing_cycle': history.subscription.billing_cycle,
#                     'status': history_status,
#                     'is_active': history.is_active,
#                 })
                
#             return Response(
#                 {'subscription_history': subscription_history_data}, 
#                 status=status.HTTP_200_OK
#             )
            
#         except Company.DoesNotExist:
#             return Response(
#                 {'error': 'Company not found'}, 
#                 status=status.HTTP_404_NOT_FOUND
#             )
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#     def stripe_webhook(self, request):
#         """
#         Handle Stripe webhook events.
        
#         Processes payment success events and updates subscription plans accordingly.
#         """
#         payload = request.body
#         sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        
#         try:
#             # Verify webhook signature
#             event = stripe.Webhook.construct_event(
#                 payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
#             )
            
#             # Handle payment success events
#             if event['type'] == 'payment_intent.succeeded':
#                 payment_intent = event['data']['object']
#                 metadata = payment_intent.metadata
                
#                 try:
#                     # Get company and tier from metadata
#                     company = Company.objects.get(id=metadata.get('company_id'))
#                     tier = SubscriptionTier.objects.get(id=metadata.get('plan_id'))
#                     billing_period = metadata.get('billing_period')
                    
#                     # Calculate dates
#                     start_date = timezone.now().date()
#                     renewal_date = start_date + timedelta(
#                         days=365 if billing_period == 'annually' else 30
#                     )
                    
#                     # Deactivate existing active plan
#                     SubscriptionPlan.objects.filter(
#                         company=company, 
#                         is_active=True
#                     ).update(is_active=False)
                    
#                     # Create new subscription plan
#                     new_plan = SubscriptionPlan.objects.create(
#                         company=company,
#                         tier=tier,
#                         billing_cycle=billing_period,
#                         start_date=start_date,
#                         renewal_date=renewal_date,
#                         is_active=True,
#                     )
                        
#                     # Create history record
#                     SubscriptionHistory.objects.create(
#                         subscription=new_plan,
#                         start_date=start_date,
#                         renewal_date=renewal_date,
#                         is_active=True
#                     )
                    
#                     return Response({'status': 'subscription updated'}, status=200)
                    
#                 except Exception as e:
#                     print(f"Error processing webhook: {str(e)}")
#                     return Response({'error': str(e)}, status=200)
                    
#             return Response({'status': 'event processed'}, status=200)
            
#         except ValueError as e:
#             return Response({'error': 'Invalid payload'}, status=400)
#         except stripe.error.SignatureVerificationError as e:
#             return Response({'error': 'Invalid signature'}, status=400)
#         except Exception as e:
#             return Response({'error': str(e)}, status=500)