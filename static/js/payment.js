document.addEventListener('DOMContentLoaded', function() {
    const stripe = Stripe('your_publishable_key');
    const submitButton = document.getElementById('submit-payment');
    const messageDiv = document.getElementById('payment-message');

    let elements;

    initialize();

    async function initialize() {
        try {
            const response = await fetch(`/create-payment-intent/${songId}`);
            const { clientSecret } = await response.json();

            elements = stripe.elements({ clientSecret });
            const paymentElement = elements.create('payment');
            paymentElement.mount('#payment-element');
        } catch (e) {
            messageDiv.textContent = 'Error initializing payment. Please try again.';
        }
    }

    submitButton.addEventListener('click', async function(e) {
        e.preventDefault();
        submitButton.disabled = true;
        
        const { error } = await stripe.confirmPayment({
            elements,
            confirmParams: {
                return_url: window.location.origin + '/payment-success',
            },
        });

        if (error) {
            messageDiv.textContent = error.message;
            submitButton.disabled = false;
        }
    });
});
