//
//  TaskCell.h
//  Task Coach
//
//  Created by Jérôme Laheurte on 03/04/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import <UIKit/UIKit.h>

@class CDTask;
@class ImageButton;

@interface TaskCell : UITableViewCell
{
    IBOutlet UILabel *mainLabel;
    IBOutlet UILabel *leftLabel;
    IBOutlet UILabel *rightLabel;
    IBOutlet ImageButton *checkView;
}

- (void)setTask:(CDTask *)task;

@end
