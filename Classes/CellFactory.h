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

@interface CellFactory : NSObject
{
	TaskCell *taskCellTemplate;
	TextFieldCell *textFieldCellTemplate;
	SwitchCell *switchCellTemplate;
}

@property (nonatomic, assign) IBOutlet TaskCell *taskCellTemplate;
@property (nonatomic, assign) IBOutlet TextFieldCell *textFieldCellTemplate;
@property (nonatomic, assign) IBOutlet SwitchCell *switchCellTemplate;

+ (CellFactory *)cellFactory;

- (TaskCell *)createTaskCell;
- (TextFieldCell *)createTextFieldCell;
- (SwitchCell *)createSwitchCell;

@end
