from django.core.paginator import Paginator
from django.db.models import CharField, F, Q, Value
from django.db.models.functions import Concat
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Employees, WorkSchedules
from .serializers import EmployeesSerializer, WorkSchedulesSerializer
#Class EmployeeDetails 
class MainEmployees(APIView):
    def get_object(self, pk):
        try:
            return Employees.objects.get(pk=pk)
        except Employees.DoesNotExist:
            raise Http404
    #Specific ID include workschedule records
    def get(self, request, pk):
        employee = self.get_object(pk)
        serializer = EmployeesSerializer(employee)
        return Response(serializer.data)

    def get(self, request):
        # Get the "keyword" parameter from the request query string, default to empty string if not present
        keyword = request.GET.get('keyword', '')
        if not keyword:
            #Get employees list
            employees = Employees.objects.all()
        # Filter the Employees queryset to include any records where the firstname, middlename, or lastname field contains the keyword
        # Also include any records where the concatenation of the firstname, middlename, and lastname fields matches the keyword
        else:
            employees = Employees.objects.filter(
                Q(firstname__icontains=keyword) |
                Q(middlename__icontains=keyword) |
                Q(lastname__icontains=keyword) |
                Q(firstname__icontains=keyword.split(' ')[0], middlename__icontains=keyword.split(' ')[1], lastname__icontains=keyword.split(' ')[2])
            )     
        # Get the "page_size" parameter from the request query string, default to 10 if not present
        page_size = request.GET.get('page_size', 10)  
        # Create a Paginator object with the filtered Employees queryset and the requested page size
        paginator = Paginator(employees, page_size)  
        # Get the "page_number" parameter from the request query string, default to 1 if not present
        page_number = request.GET.get('page_number', 1) 
        # Get a Page object for the requested page number from the Paginator object
        employees_page = paginator.get_page(page_number)
        # Serialize the Page object using the EmployeesSerializer
        serializer = EmployeesSerializer(employees_page, many=True)
        # Return the serialized data in a Response object
        return Response(serializer.data)

    def post(self, request):
        serializer = EmployeesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        employee = self.get_object(pk)
        serializer = EmployeesSerializer(employee, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        employee = self.get_object(pk)
        employee.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

#Class EmployeesRegularization checks if regular employee
class EmployeesRegularization(APIView):
    def get_object(self, pk):
        try:
            return Employees.objects.get(pk=pk)
        except Employees.DoesNotExist:
            return Response({'error': 'employee record does not exist'}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, pk):
        employee = self.get_object(pk)
        is_regular = request.data.get('isRegular')
        regularization_date = request.data.get('RegularizationDate')

        # Check if both columns are supplied
        if is_regular is None or regularization_date is None:
            return Response({'error': 'Both isRegular and RegularizationDate must be supplied.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the employee is already set as regular
        if employee.isRegular and employee.RegularizationDate is not None:
            return Response({'error': 'Employee is already set as regular.'}, status=status.HTTP_400_BAD_REQUEST)

        # Update the employee record
        serializer = EmployeesSerializer(employee, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# class WorkSchedulesView List Employees's WorkSchedules Define a view to handle creating work schedules
class WorkSchedulesView(APIView):

    # This is a view method for handling HTTP GET requests. It expects a request object
    # as its first argument, and an optional 'format' parameter.
    def get(self, request, format=None):
        
        # Retrieve all WorkSchedules objects from the database.
        work_schedules = WorkSchedules.objects.all()
        
        # Serialize the WorkSchedules queryset into JSON format using the
        # WorkSchedulesSerializer class. The 'many=True' parameter indicates that
        # we're serializing multiple objects, rather than a single one.
        serializer = WorkSchedulesSerializer(work_schedules, many=True)
        
        # Return the serialized data in an HTTP response with the 'Response' class.
        return Response(serializer.data)

    def post(self, request):
        try:
            # Get the data from the request
            workschedules_data = request.data
            # Get a list of employee IDs from the workschedule data
            employee_id_list = [int(workschedule['employee']) for workschedule in workschedules_data]
            # Delete any existing workschedules for the specified employees
            existing_workschedules = WorkSchedules.objects.filter(employee_id__in=employee_id_list)
            existing_workschedules.delete()

            # Create a serializer for the workschedule data
            workschedules_serializer = WorkSchedulesSerializer(data=workschedules_data, many=True)

            # If the serializer is valid, save the data and return a success response
            if workschedules_serializer.is_valid():
                workschedules_serializer.save()
                return Response(workschedules_serializer.data, status=status.HTTP_201_CREATED)
            else:
                # If the serializer is not valid, return an error response
                return Response(workschedules_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # If an error occurs, return a server error response
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
