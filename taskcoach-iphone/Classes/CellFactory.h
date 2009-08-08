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

@interface CellFactory : NSObject
{
	TaskCell *taskCellTemplate;
	TextFieldCell *textFieldCellTemplate;
	SwitchCell *switchCellTemplate;
	DateCell *dateCellTemplate;
	DescriptionCell *descriptionCellTemplate;
}

@property (nonatomic, assign) IBOutlet TaskCell *taskCellTemplate;
@property (nonatomic, assign) IBOutlet TextFieldCell *textFieldCellTemplate;
@property (nonatomic, assign) IBOutlet SwitchCell *switchCellTemplate;
@property (nonatomic, assign) IBOutlet DateCell *dateCellTemplate;
@property (nonatomic, assign) IBOutlet DescriptionCell *descriptionCellTemplate;

+ (CellFactory *)cellFactory;

- (TaskCell *)createTaskCell;
- (TextFieldCell *)createTextFieldCell;
- (SwitchCell *)createSwitchCell;
- (DateCell *)createDateCell;
- (DescriptionCell *)createDescriptionCell;

@end
