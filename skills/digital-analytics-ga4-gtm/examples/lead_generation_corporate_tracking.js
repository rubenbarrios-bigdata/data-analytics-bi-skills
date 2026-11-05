/**
 * Implementación de Eventos Corporativos y Lead Generation para GA4
 * Autor: Rubén David Barrios Bello - Data Analyst & BI Developer
 */

// 1. Envío de Formulario de Contacto / Prospecto Comercial (generate_lead)
function trackLeadFormSubmission(formElement) {
  window.dataLayer = window.dataLayer || [];
  window.dataLayer.push({
    event: "generate_lead",
    lead_type: "consulting_service",
    lead_channel: "website_contact_form",
    lead_qualification: "high_priority",
    estimated_deal_value: 2500.00,
    currency: "USD"
  });
}

// 2. Descarga de Material Técnico / Caso de Estudio (file_download customizado)
function trackAssetDownload(fileName, fileType) {
  window.dataLayer = window.dataLayer || [];
  window.dataLayer.push({
    event: "asset_download",
    file_name: fileName,
    file_extension: fileType,
    asset_category: "whitepaper_bi_devops",
    user_status: "anonymous_lead"
  });
}

// 3. Reserva o Agendamiento de Reunión / Cita Comercial
function trackAppointmentScheduled(appointmentId, meetingTopic) {
  window.dataLayer = window.dataLayer || [];
  window.dataLayer.push({
    event: "schedule_appointment",
    appointment_id: appointmentId,
    service_line: meetingTopic,
    appointment_medium: "google_meet"
  });
}

