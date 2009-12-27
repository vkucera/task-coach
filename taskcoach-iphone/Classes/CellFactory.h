//
//  CellFactory.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 17/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import <Foundation/Foundation.h>

@class TaskCell;
@class TextFieldCell;
@class SwitchCell;
@class DateCell;
@class DescriptionCell;
@class BadgedCell;
@class ButtonCell;

@interface CellFactory : NSObject
{
	TaskCell *taskCellTemplate;
	TextFieldCell *textFieldCellTemplate;
	SwitchCell *switchCellTemplate;
	DateCell *dateCellTemplate;
	DescriptionCell *descriptionCellTemplate;
	BadgedCell *badgedCellTemplate;
	ButtonCell *buttonCellTemplate;
}

@property (nonatomic, assign) IBOutlet TaskCell *taskCellTemplate;
@property (nonatomic, assign) IBOutlet TextFieldCell *textFieldCellTemplate;
@property (nonatomic, assign) IBOutlet SwitchCell *switchCellTemplate;
@property (nonatomic, assign) IBOutlet DateCell *dateCellTemplate;
@property (nonatomic, assign) IBOutlet DescriptionCell *descriptionCellTemplate;
@property (nonatomic, assign) IBOutlet BadgedCell *badgedCellTemplate;
@property (nonatomic, assign) IBOutlet ButtonCell *buttonCellTemplate;

+ (CellFactory *)cellFactory;

- (TaskCell *)createTaskCell;
- (TextFieldCell *)createTextFieldCell;
- (SwitchCell *)createSwitchCell;
- (DateCell *)createDateCell;
- (DescriptionCell *)createDescriptionCell;
- (BadgedCell *)createBadgedCell;
- (ButtonCell *)createButtonCell;

@end
