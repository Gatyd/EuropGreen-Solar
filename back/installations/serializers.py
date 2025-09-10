from rest_framework import serializers
from .models import (
	Form,
	Signature,
	TechnicalVisit,
	RepresentationMandate,
	AdministrativeValidation,
	InstallationCompleted,
	ConsuelVisit,
	EnedisConnection,
	Commissioning
)
from administrative.serializers import Cerfa16702Serializer, ElectricalDiagramSerializer, EnedisMandateSerializer
from invoices.serializers import InvoiceSerializer
from billing.serializers import QuotePDFSerializer
from offers.serializers import OfferBaseSerializer

class SignatureSerializer(serializers.ModelSerializer):
	class Meta:
		model = Signature
		fields = [
			'id', 'signer_name', 'ip_address', 'user_agent', 'signed_at', 'signature_image', 'created_at'
		]

class TechnicalVisitSerializer(serializers.ModelSerializer):
	client_signature = SignatureSerializer(read_only=True)
	installer_signature = SignatureSerializer(read_only=True)

	class Meta:
		model = TechnicalVisit
		fields = [
			'id', 'visit_date', 'expected_installation_date',
			'roof_type', 'tiles_spare_provided', 'roof_shape',
			'roof_access', 'roof_access_other',
			'truck_access', 'truck_access_comment', 'nacelle_needed',
			'meter_type', 'meter_type_other', 'current_type', 'existing_grid_connection',
			'meter_position', 'meter_location_photo',
			'panels_to_board_distance_m',
			'additional_equipment_needed', 'additional_equipment_details',
			'is_validated', 'validated_at', 'approval_statement',
			'report_pdf',
			'client_signature', 'installer_signature',
			'created_at', 'updated_at'
		]

class RepresentationMandateSerializer(serializers.ModelSerializer):
	client_signature = SignatureSerializer(read_only=True)
	installer_signature = SignatureSerializer(read_only=True)

	class Meta:
		model = RepresentationMandate
		fields = [
			'id',
			'client_civility', 'client_birth_date', 'client_birth_place', 'client_address',
			'company_name', 'company_rcs_city', 'company_siret', 'company_head_office_address',
			'represented_by', 'representative_role',
			'client_signature', 'installer_signature',
			'mandate_pdf', 'created_at', 'updated_at'
		]

class AdministrativeValidationSerializer(serializers.ModelSerializer):
	class Meta:
		model = AdministrativeValidation
		fields = ['id', 'is_validated', 'validated_at', 'created_at', 'updated_at']

class InstallationCompletedSerializer(serializers.ModelSerializer):
	client_signature = SignatureSerializer(read_only=True)
	installer_signature = SignatureSerializer(read_only=True)

	class Meta:
		model = InstallationCompleted
		fields = [
			'id', 'modules_installed', 'inverters_installed', 'dc_ac_box_installed', 'battery_installed',
			'photo_modules', 'photo_inverter',
			'client_signature', 'installer_signature', 'report_pdf',
			'created_at', 'updated_at'
		]

class ConsuelVisitSerializer(serializers.ModelSerializer):
	class Meta:
		model = ConsuelVisit
		fields = ['id', 'passed', 'refusal_reason', 'created_at', 'updated_at']

class EnedisConnectionSerializer(serializers.ModelSerializer):
	class Meta:
		model = EnedisConnection
		fields = ['id', 'is_validated', 'validated_at']

class CommissioningSerializer(serializers.ModelSerializer):
	class Meta:
		model = Commissioning
		fields = '__all__'

class UserMiniSerializer(serializers.Serializer):
	id = serializers.CharField()
	first_name = serializers.CharField()
	last_name = serializers.CharField()
	email = serializers.EmailField()

class FormSerializer(serializers.ModelSerializer):
	class Meta:
		model = Form
		fields = [
			'id', 'offer', 'client_first_name', 'client_last_name', 'client_address',
			'installation_power', 'installation_type', 'status',
			'created_by', 'created_at', 'updated_at',
		]
		read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

class FormDetailSerializer(serializers.ModelSerializer):
	created_by = UserMiniSerializer(read_only=True)
	client = UserMiniSerializer(read_only=True)
	technical_visit = TechnicalVisitSerializer(read_only=True)
	representation_mandate = RepresentationMandateSerializer(read_only=True)
	administrative_validation = AdministrativeValidationSerializer(read_only=True)
	installation_completed = InstallationCompletedSerializer(read_only=True)
	consuel_visit = ConsuelVisitSerializer(read_only=True)
	enedis_connection = EnedisConnectionSerializer(read_only=True)
	commissioning = CommissioningSerializer(read_only=True)
	invoice = InvoiceSerializer(read_only=True)
	offer = OfferBaseSerializer(read_only=True)

	# Documents administratifs
	cerfa16702 = Cerfa16702Serializer(read_only=True)
	electrical_diagram = ElectricalDiagramSerializer(read_only=True)
	enedis_mandate = EnedisMandateSerializer(read_only=True)

	# Devis
	quotes = serializers.SerializerMethodField()

	class Meta:
		model = Form
		fields = [
			'id', 'offer', 'client_first_name', 'client_last_name', 'client_address',
			'installation_power', 'installation_type', 'status',
			'created_by', 'client', 'created_at', 'updated_at',
			'technical_visit', 'representation_mandate', 'administrative_validation',
			'installation_completed', 'consuel_visit', 'enedis_connection', 'commissioning',
			'cerfa16702', 'electrical_diagram', 'enedis_mandate', 'quotes', 'invoice'
		]

	def get_quotes(self, obj):
		offer = getattr(obj, 'offer', None)
		if not offer:
			return None
		if hasattr(offer, 'quotes'):
			quotes = offer.quotes.order_by('-version', '-created_at')
		if quotes:
			return QuotePDFSerializer(quotes, many=True, context=self.context).data
		return None
