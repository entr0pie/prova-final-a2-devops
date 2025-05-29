<?php

$ORDER_API_URL = getenv('ORDER_API_URL');

$request_uri = $_SERVER['REQUEST_URI'];

if ($request_uri === '/payment') {
    $orderJson = file_get_contents($ORDER_API_URL . '/order');
    $orderData = json_decode($orderJson, true);

    $response = [
        'status' => 'paid',
        'order' => $orderData
    ];

    header('Content-Type: application/json');
    echo json_encode($response);
} else {
    http_response_code(404);
    echo json_encode(['error' => 'Not found']);
}

?>