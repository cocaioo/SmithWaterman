import numpy as np

POINTER_STOP = 0
POINTER_LEFT = 1
POINTER_DIAGONAL = 2
POINTER_UP = 3
POINTER_LEFT_DIAGONAL = 4
POINTER_LEFT_UP = 5
POINTER_DIAGONAL_UP = 6
POINTER_ALL = 7
EPSILON = 1e-9


def openFilee(file_path):
    with open(file_path, encoding='utf-8') as input_file:
        lines = input_file.readlines()
    return lines


def parseInput(lines):
    vertical_sequence = lines[0].strip()
    horizontal_sequence = lines[1].strip()
    gap_penalty = float(lines[2])
    mismatch_penalty = float(lines[3])
    match_score = float(lines[4])
    return vertical_sequence, horizontal_sequence, gap_penalty, mismatch_penalty, match_score


def getMatrixDimensions(vertical_sequence, horizontal_sequence):
    row_count = int(len(vertical_sequence) + 1)
    column_count = int(len(horizontal_sequence) + 1)
    return row_count, column_count


def createMatrix(row_count, column_count):
    matrix = np.zeros((row_count, column_count))
    return matrix


def setGapsHorizontal(matrix, gap_penalty):
    last_row = matrix.shape[0] - 1
    for column in range(matrix.shape[1]):
        matrix[last_row, column] = column * gap_penalty
    return matrix


def setGapsVertical(matrix, gap_penalty):
    last_row = matrix.shape[0] - 1
    for row in range(matrix.shape[0]):
        matrix[last_row - row, 0] = row * gap_penalty
    return matrix


def initializeMatrixWithGaps(row_count, column_count, gap_penalty):
    matrix = createMatrix(row_count, column_count)
    matrix = setGapsHorizontal(matrix, gap_penalty)
    matrix = setGapsVertical(matrix, gap_penalty)
    return matrix


def isMatch(vertical_sequence, horizontal_sequence, row, column):
    vertical_index = (len(vertical_sequence) - 1) - row
    horizontal_index = column - 1
    return vertical_sequence[vertical_index] == horizontal_sequence[horizontal_index]


def encodePointer(from_left, from_diagonal, from_up):
    # Permite empate: combina direcoes conforme o melhor score.
    if from_left and from_diagonal and from_up:
        return POINTER_ALL
    if from_left and from_diagonal:
        return POINTER_LEFT_DIAGONAL
    if from_left and from_up:
        return POINTER_LEFT_UP
    if from_diagonal and from_up:
        return POINTER_DIAGONAL_UP
    if from_left:
        return POINTER_LEFT
    if from_diagonal:
        return POINTER_DIAGONAL
    if from_up:
        return POINTER_UP
    return POINTER_STOP


def isSameScore(value_a, value_b):
    return np.isclose(value_a, value_b, atol=EPSILON)


def decodePointer(pointer_value):
    can_go_left = pointer_value in (POINTER_LEFT, POINTER_LEFT_DIAGONAL, POINTER_LEFT_UP, POINTER_ALL)
    can_go_diagonal = pointer_value in (POINTER_DIAGONAL, POINTER_LEFT_DIAGONAL, POINTER_DIAGONAL_UP, POINTER_ALL)
    can_go_up = pointer_value in (POINTER_UP, POINTER_LEFT_UP, POINTER_DIAGONAL_UP, POINTER_ALL)
    return can_go_left, can_go_diagonal, can_go_up


def chooseTracebackDirection(pointer_value, score_matrix, row, column):
    can_go_left, can_go_diagonal, can_go_up = decodePointer(pointer_value)

    candidates = []

    if can_go_left and column - 1 >= 0:
        candidates.append(('left', score_matrix[row, column - 1]))

    if can_go_diagonal and row + 1 < score_matrix.shape[0] and column - 1 >= 0:
        candidates.append(('diagonal', score_matrix[row + 1, column - 1]))

    if can_go_up and row + 1 < score_matrix.shape[0]:
        candidates.append(('up', score_matrix[row + 1, column]))

    if not candidates:
        return None

    max_neighbor_value = max(value for _, value in candidates)
    best_directions = [direction for direction, value in candidates if value == max_neighbor_value]

    for preferred_direction in ('diagonal', 'up', 'left'):
        if preferred_direction in best_directions:
            return preferred_direction

    return best_directions[0]


def computeCandidateScores(score_matrix, row, column, gap_penalty, mismatch_penalty, match_score, vertical_sequence, horizontal_sequence):
    left_score = score_matrix[row, column - 1] + gap_penalty

    if isMatch(vertical_sequence, horizontal_sequence, row, column):
        diagonal_score = score_matrix[row + 1, column - 1] + match_score
    else:
        diagonal_score = score_matrix[row + 1, column - 1] + mismatch_penalty

    up_score = score_matrix[row + 1, column] + gap_penalty
    return left_score, diagonal_score, up_score


def buildGlobalMatrices(vertical_sequence, horizontal_sequence, gap_penalty, mismatch_penalty, match_score):
    row_count, column_count = getMatrixDimensions(vertical_sequence, horizontal_sequence)
    score_matrix = initializeMatrixWithGaps(row_count, column_count, gap_penalty)
    pointer_matrix = np.zeros((row_count, column_count), dtype=int)

    for row in range(row_count - 2, -1, -1):
        for column in range(1, column_count):
            left_score, diagonal_score, up_score = computeCandidateScores(
                score_matrix,
                row,
                column,
                gap_penalty,
                mismatch_penalty,
                match_score,
                vertical_sequence,
                horizontal_sequence,
            )

            best_score = max(left_score, diagonal_score, up_score)
            score_matrix[row, column] = best_score

            pointer_matrix[row, column] = encodePointer(
                isSameScore(left_score, best_score),
                isSameScore(diagonal_score, best_score),
                isSameScore(up_score, best_score),
            )

    return score_matrix, pointer_matrix


def buildLocalMatrices(vertical_sequence, horizontal_sequence, gap_penalty, mismatch_penalty, match_score):
    row_count, column_count = getMatrixDimensions(vertical_sequence, horizontal_sequence)
    score_matrix = createMatrix(row_count, column_count)
    pointer_matrix = np.zeros((row_count, column_count), dtype=int)

    for row in range(row_count - 2, -1, -1):
        for column in range(1, column_count):
            left_score, diagonal_score, up_score = computeCandidateScores(
                score_matrix,
                row,
                column,
                gap_penalty,
                mismatch_penalty,
                match_score,
                vertical_sequence,
                horizontal_sequence,
            )

            best_score = max(0, left_score, diagonal_score, up_score)
            score_matrix[row, column] = best_score

            if isSameScore(best_score, 0.0):
                pointer_matrix[row, column] = POINTER_STOP
                continue

            pointer_matrix[row, column] = encodePointer(
                isSameScore(left_score, best_score),
                isSameScore(diagonal_score, best_score),
                isSameScore(up_score, best_score),
            )

    return score_matrix, pointer_matrix


def buildAlignmentFromPosition(score_matrix, pointer_matrix, vertical_sequence, horizontal_sequence, start_row, start_column, stop_at_zero, complete_boundaries):
    aligned_vertical = []
    aligned_horizontal = []

    row = start_row
    column = start_column
    last_row = score_matrix.shape[0] - 1

    while 0 <= row <= last_row and column >= 0:
        if stop_at_zero and score_matrix[row, column] <= 0:
            break

        if row == last_row and column == 0:
            break

        if column == 0:
            if not complete_boundaries:
                break
            vertical_index = (len(vertical_sequence) - 1) - row
            aligned_vertical.append(vertical_sequence[vertical_index])
            aligned_horizontal.append('-')
            row += 1
            continue

        if row == last_row:
            if not complete_boundaries:
                break
            horizontal_index = column - 1
            aligned_vertical.append('-')
            aligned_horizontal.append(horizontal_sequence[horizontal_index])
            column -= 1
            continue

        pointer_value = int(pointer_matrix[row, column])
        direction = chooseTracebackDirection(pointer_value, score_matrix, row, column)

        if direction is None:
            if not complete_boundaries:
                break

            fallback_candidates = []

            if column - 1 >= 0:
                fallback_candidates.append(('left', score_matrix[row, column - 1]))

            if row + 1 <= last_row and column - 1 >= 0:
                fallback_candidates.append(('diagonal', score_matrix[row + 1, column - 1]))

            if row + 1 <= last_row:
                fallback_candidates.append(('up', score_matrix[row + 1, column]))

            if not fallback_candidates:
                break

            max_neighbor_value = max(value for _, value in fallback_candidates)
            best_directions = [
                fallback_direction
                for fallback_direction, value in fallback_candidates
                if isSameScore(value, max_neighbor_value)
            ]

            direction = best_directions[0]
            for preferred_direction in ('diagonal', 'up', 'left'):
                if preferred_direction in best_directions:
                    direction = preferred_direction
                    break

        vertical_index = (len(vertical_sequence) - 1) - row
        horizontal_index = column - 1

        if direction == 'diagonal':
            aligned_vertical.append(vertical_sequence[vertical_index])
            aligned_horizontal.append(horizontal_sequence[horizontal_index])
            row += 1
            column -= 1
        elif direction == 'left':
            aligned_vertical.append('-')
            aligned_horizontal.append(horizontal_sequence[horizontal_index])
            column -= 1
        elif direction == 'up':
            aligned_vertical.append(vertical_sequence[vertical_index])
            aligned_horizontal.append('-')
            row += 1

    aligned_vertical.reverse()
    aligned_horizontal.reverse()
    return ''.join(aligned_vertical), ''.join(aligned_horizontal)


def findBestLocalPosition(local_score_matrix):
    best_position = np.unravel_index(np.argmax(local_score_matrix), local_score_matrix.shape)
    return int(best_position[0]), int(best_position[1])


def alinhamentoGlobal(global_score_matrix, global_pointer_matrix, vertical_sequence, horizontal_sequence):
    start_row = 0
    start_column = global_score_matrix.shape[1] - 1
    return buildAlignmentFromPosition(
        global_score_matrix,
        global_pointer_matrix,
        vertical_sequence,
        horizontal_sequence,
        start_row,
        start_column,
        stop_at_zero=False,
        complete_boundaries=True,
    )


def alinhamentoLocal(local_score_matrix, local_pointer_matrix, vertical_sequence, horizontal_sequence):
    start_row, start_column = findBestLocalPosition(local_score_matrix)
    return buildAlignmentFromPosition(
        local_score_matrix,
        local_pointer_matrix,
        vertical_sequence,
        horizontal_sequence,
        start_row,
        start_column,
        stop_at_zero=False,
        complete_boundaries=True,
    )


def alinhamentoMelhorScore(local_score_matrix, local_pointer_matrix, vertical_sequence, horizontal_sequence):
    start_row, start_column = findBestLocalPosition(local_score_matrix)
    best_score = float(local_score_matrix[start_row, start_column])

    aligned_vertical, aligned_horizontal = buildAlignmentFromPosition(
        local_score_matrix,
        local_pointer_matrix,
        vertical_sequence,
        horizontal_sequence,
        start_row,
        start_column,
        stop_at_zero=False,
        complete_boundaries=True,
    )

    return aligned_vertical, aligned_horizontal, best_score


def traceBack(local_score_matrix, local_pointer_matrix, vertical_sequence, horizontal_sequence, global_score_matrix=None, global_pointer_matrix=None):
    if global_score_matrix is not None and global_pointer_matrix is not None:
        global_vertical, global_horizontal = alinhamentoGlobal(
            global_score_matrix,
            global_pointer_matrix,
            vertical_sequence,
            horizontal_sequence,
        )
    else:
        global_vertical, global_horizontal = '', ''

    local_vertical, local_horizontal = alinhamentoLocal(
        local_score_matrix,
        local_pointer_matrix,
        vertical_sequence,
        horizontal_sequence,
    )
    best_vertical, best_horizontal, best_score = alinhamentoMelhorScore(
        local_score_matrix,
        local_pointer_matrix,
        vertical_sequence,
        horizontal_sequence,
    )

    return {
        'global_vertical': global_vertical,
        'global_horizontal': global_horizontal,
        'local_vertical': local_vertical,
        'local_horizontal': local_horizontal,
        'best_vertical': best_vertical,
        'best_horizontal': best_horizontal,
        'best_score': best_score,
    }


def SmithWaterman(score_matrix, gap_penalty, mismatch_penalty, match_score, vertical_sequence, horizontal_sequence):
    row_count, column_count = score_matrix.shape
    _ = row_count, column_count
    local_score_matrix, local_pointer_matrix = buildLocalMatrices(
        vertical_sequence,
        horizontal_sequence,
        gap_penalty,
        mismatch_penalty,
        match_score,
    )
    return local_score_matrix, local_pointer_matrix


def runAlignmentSuite(vertical_sequence, horizontal_sequence, gap_penalty, mismatch_penalty, match_score):
    global_score_matrix, global_pointer_matrix = buildGlobalMatrices(
        vertical_sequence,
        horizontal_sequence,
        gap_penalty,
        mismatch_penalty,
        match_score,
    )
    local_score_matrix, local_pointer_matrix = buildLocalMatrices(
        vertical_sequence,
        horizontal_sequence,
        gap_penalty,
        mismatch_penalty,
        match_score,
    )

    alignment_result = traceBack(
        local_score_matrix,
        local_pointer_matrix,
        vertical_sequence,
        horizontal_sequence,
        global_score_matrix,
        global_pointer_matrix,
    )

    alignment_result['global_score_matrix'] = global_score_matrix
    alignment_result['global_pointer_matrix'] = global_pointer_matrix
    alignment_result['local_score_matrix'] = local_score_matrix
    alignment_result['local_pointer_matrix'] = local_pointer_matrix

    return alignment_result


if __name__ == '__main__':
    input_lines = openFilee('input.txt')

    vertical_sequence, horizontal_sequence, gap_penalty, mismatch_penalty, match_score = parseInput(input_lines)
    result = runAlignmentSuite(
        vertical_sequence,
        horizontal_sequence,
        gap_penalty,
        mismatch_penalty,
        match_score,
    )

    print(result['global_score_matrix'])
    print(result['global_pointer_matrix'])
    print(result['local_score_matrix'])
    print(result['local_pointer_matrix'])
    print({
        'global_vertical': result['global_vertical'],
        'global_horizontal': result['global_horizontal'],
        'local_vertical': result['local_vertical'],
        'local_horizontal': result['local_horizontal'],
        'best_vertical': result['best_vertical'],
        'best_horizontal': result['best_horizontal'],
        'best_score': result['best_score'],
    })
