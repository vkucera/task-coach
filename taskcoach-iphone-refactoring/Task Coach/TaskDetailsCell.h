//
//  TaskDetailsCell.h
//  Task Coach
//
//  Created by Jérôme Laheurte on 09/04/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import <UIKit/UIKit.h>

#import "ImageButton.h"
#import "SmartButton.h"

@class CDTask;

@interface TaskDetailsCell : UITableViewCell
{
    IBOutlet UITextField *subject;
    IBOutlet ImageButton *completionButton;
    IBOutlet SmartButton *trackButton;
    IBOutlet SmartButton *doneButton;

    void (^callback)(id);
}

- (void)setTask:(CDTask *)task callback:(void (^)(id))callback;

@end
