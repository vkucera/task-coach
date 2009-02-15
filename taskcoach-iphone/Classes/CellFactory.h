//
//  CellFactory.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 17/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import <Foundation/Foundation.h>

@class TaskCell;
@class TextFieldCell;
@class SwitchCell;
@class DescriptionCell;

@interface CellFactory : NSObject
{
	TaskCell *taskCellTemplate;
	TextFieldCell *textFieldCellTemplate;
	SwitchCell *switchCellTemplate;
	DescriptionCell *descriptionCellTemplate;
}

@property (nonatomic, assign) IBOutlet TaskCell *taskCellTemplate;
@property (nonatomic, assign) IBOutlet TextFieldCell *textFieldCellTemplate;
@property (nonatomic, assign) IBOutlet SwitchCell *switchCellTemplate;
@property (nonatomic, assign) IBOutlet DescriptionCell *descriptionCellTemplate;

+ (CellFactory *)cellFactory;

- (TaskCell *)createTaskCell;
- (TextFieldCell *)createTextFieldCell;
- (SwitchCell *)createSwitchCell;
- (DescriptionCell *)createDescriptionCell;

@end
