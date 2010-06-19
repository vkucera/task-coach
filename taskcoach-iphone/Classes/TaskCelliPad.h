//
//  TaskCelliPad.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 19/06/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import <Foundation/Foundation.h>

#import "TaskCellBig.h"

@interface TaskCelliPad : TaskCellBig
{
	UILabel *priorityLabel;
	UITextView *descriptionView;
}

@property (nonatomic, retain) IBOutlet UILabel *priorityLabel;
@property (nonatomic, retain) IBOutlet UITextView *descriptionView;

@end
